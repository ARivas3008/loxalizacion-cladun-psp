//go:build windows

// Native Win32 front end. No Python, .NET, C runtime or third-party GUI DLLs.
package main

import (
	"fmt"
	"runtime"
	"strings"
	"sync"
	"syscall"
	"unicode/utf16"
	"unsafe"

	"github.com/ARivas3008/loxalizacion-cladun-psp/patcher/internal/automatic"
	"github.com/ARivas3008/loxalizacion-cladun-psp/patcher/internal/bps"
)

var (
	kernel32            = syscall.NewLazyDLL("kernel32.dll")
	user32              = syscall.NewLazyDLL("user32.dll")
	gdi32               = syscall.NewLazyDLL("gdi32.dll")
	comdlg32            = syscall.NewLazyDLL("comdlg32.dll")
	procGetModuleHandle = kernel32.NewProc("GetModuleHandleW")
	procCreateWindow    = user32.NewProc("CreateWindowExW")
	procDefWindowProc   = user32.NewProc("DefWindowProcW")
	procRegisterClass   = user32.NewProc("RegisterClassExW")
	procGetMessage      = user32.NewProc("GetMessageW")
	procTranslate       = user32.NewProc("TranslateMessage")
	procDispatch        = user32.NewProc("DispatchMessageW")
	procPostQuit        = user32.NewProc("PostQuitMessage")
	procPostMessage     = user32.NewProc("PostMessageW")
	procSendMessage     = user32.NewProc("SendMessageW")
	procLoadCursor      = user32.NewProc("LoadCursorW")
	procLoadIcon        = user32.NewProc("LoadIconW")
	procShowWindow      = user32.NewProc("ShowWindow")
	procUpdateWindow    = user32.NewProc("UpdateWindow")
	procEnableWindow    = user32.NewProc("EnableWindow")
	procSetWindowText   = user32.NewProc("SetWindowTextW")
	procGetWindowText   = user32.NewProc("GetWindowTextW")
	procGetTextLength   = user32.NewProc("GetWindowTextLengthW")
	procMessageBox      = user32.NewProc("MessageBoxW")
	procInvalidate      = user32.NewProc("InvalidateRect")
	procSetTimer        = user32.NewProc("SetTimer")
	procKillTimer       = user32.NewProc("KillTimer")
	procBeginPaint      = user32.NewProc("BeginPaint")
	procEndPaint        = user32.NewProc("EndPaint")
	procFillRect        = user32.NewProc("FillRect")
	procSetBkMode       = gdi32.NewProc("SetBkMode")
	procSetTextColor    = gdi32.NewProc("SetTextColor")
	procCreateBrush     = gdi32.NewProc("CreateSolidBrush")
	procCreateFont      = gdi32.NewProc("CreateFontW")
	procDeleteObject    = gdi32.NewProc("DeleteObject")
	procGetOpenFile     = comdlg32.NewProc("GetOpenFileNameW")
	procGetSaveFile     = comdlg32.NewProc("GetSaveFileNameW")
	procCommDlgError    = comdlg32.NewProc("CommDlgExtendedError")
)

const (
	wsOverlappedWindow = 0x00CF0000
	wsVisible          = 0x10000000
	wsChild            = 0x40000000
	wsClipChildren     = 0x02000000
	wsTabstop          = 0x00010000
	wsBorder           = 0x00800000
	esAutoHScroll      = 0x0080
	wmCreate           = 0x0001
	wmDestroy          = 0x0002
	wmPaint            = 0x000F
	wmCommand          = 0x0111
	wmTimer            = 0x0113
	wmSetFont          = 0x0030
	wmCtlColorStatic   = 0x0138
	wmAppDone          = 0x8001
	swShow             = 5
	colorTransparent   = 1
	ofnExplorer        = 0x00080000
	ofnPathMustExist   = 0x00000800
	ofnFileMustExist   = 0x00001000
	ofnNoChangeDir     = 0x00000008
	idISO              = 101
	idApply            = 104
	timerID            = 1
)

// Win32 structs use native pointer width and field alignment.
type point struct{ X, Y int32 }
type rect struct{ L, T, R, B int32 }
type msg struct {
	Hwnd     uintptr
	Message  uint32
	_        uint32
	WParam   uintptr
	LParam   uintptr
	Time     uint32
	Pt       point
	LPrivate uint32
}
type wndClassEx struct {
	Size       uint32
	Style      uint32
	WndProc    uintptr
	ClsExtra   int32
	WndExtra   int32
	Instance   uintptr
	Icon       uintptr
	Cursor     uintptr
	Background uintptr
	MenuName   *uint16
	ClassName  *uint16
	IconSm     uintptr
}
type paintStruct struct {
	Hdc       uintptr
	Erase     int32
	Area      rect
	Restore   int32
	IncUpdate int32
	Reserved  [32]byte
}
type openFileName struct {
	StructSize      uint32
	Owner           uintptr
	Instance        uintptr
	Filter          *uint16
	CustomFilter    *uint16
	MaxCustomFilter uint32
	FilterIndex     uint32
	File            *uint16
	MaxFile         uint32
	FileTitle       *uint16
	MaxFileTitle    uint32
	InitialDir      *uint16
	Title           *uint16
	Flags           uint32
	FileOffset      uint16
	FileExtension   uint16
	DefExt          *uint16
	CustData        uintptr
	Hook            uintptr
	TemplateName    *uint16
	Reserved        uintptr
	ReservedDWORD   uint32
	FlagsEx         uint32
}

type application struct {
	hwnd                                                    uintptr
	iso                                                     uintptr
	apply, isoBrowse                                        uintptr
	status                                                  uintptr
	headTitle, headBrand, headCaption                       uintptr
	editFont, headFont, titleFont, labelFont, smallFont     uintptr
	bgBrush, whiteBrush, headerBrush, barBrush, borderBrush uintptr
	textHandles                                             map[uintptr]uint32
	mu                                                      sync.Mutex
	phase                                                   string
	progress                                                int
	busy                                                    bool
	result                                                  bps.Info
	resultOutput                                            string
	failure                                                 error
	finished                                                bool
}

var app application

func u16(s string) *uint16                              { return syscall.StringToUTF16Ptr(s) }
func call(proc *syscall.LazyProc, a ...uintptr) uintptr { r, _, _ := proc.Call(a...); return r }

// COLORREF is 0x00BBGGRR.
func rgb(r, g, b uint32) uintptr { return uintptr(r | g<<8 | b<<16) }

func createCtrl(class, value string, style, exstyle uint32, x, y, width, height int32, id int32) uintptr {
	return call(procCreateWindow, uintptr(exstyle), uintptr(unsafe.Pointer(u16(class))), uintptr(unsafe.Pointer(u16(value))), uintptr(style|wsVisible|wsChild), uintptr(x), uintptr(y), uintptr(width), uintptr(height), app.hwnd, uintptr(id), 0, 0)
}
func setFont(hwnd, font uintptr) { call(procSendMessage, hwnd, wmSetFont, font, 1) }
func label(s string, x, y, width, height int32, font uintptr, color uint32) uintptr {
	w := createCtrl("STATIC", s, 0, 0, x, y, width, height, 0)
	setFont(w, font)
	app.textHandles[w] = color
	return w
}
func edit(x, y int32) uintptr {
	w := createCtrl("EDIT", "", wsBorder|wsTabstop|esAutoHScroll, 0, x, y, 520, 30, 0)
	setFont(w, app.editFont)
	return w
}
func button(s string, x, y, width, height int32, id int32, font uintptr) uintptr {
	w := createCtrl("BUTTON", s, wsTabstop, 0, x, y, width, height, id)
	setFont(w, font)
	return w
}
func setText(w uintptr, s string) { call(procSetWindowText, w, uintptr(unsafe.Pointer(u16(s)))) }
func getText(w uintptr) string {
	n := call(procGetTextLength, w)
	if n > 32767 {
		return ""
	}
	buf := make([]uint16, n+1)
	call(procGetWindowText, w, uintptr(unsafe.Pointer(&buf[0])), uintptr(len(buf)))
	return syscall.UTF16ToString(buf)
}
func createFont(height int32, bold bool) uintptr {
	weight := uintptr(400)
	if bold {
		weight = 700
	}
	return call(procCreateFont, uintptr(int64(height)), 0, 0, 0, weight, 0, 0, 0, 1, 0, 0, 5, 0, uintptr(unsafe.Pointer(u16("Segoe UI"))))
}
func showError(title, message string) {
	call(procMessageBox, app.hwnd, uintptr(unsafe.Pointer(u16(message))), uintptr(unsafe.Pointer(u16(title))), 0x10)
}
func showInfo(title, message string) {
	call(procMessageBox, app.hwnd, uintptr(unsafe.Pointer(u16(message))), uintptr(unsafe.Pointer(u16(title))), 0x40)
}

func createUI(hwnd uintptr) {
	app.hwnd = hwnd
	app.textHandles = make(map[uintptr]uint32)
	app.bgBrush = call(procCreateBrush, rgb(243, 246, 251))
	app.whiteBrush = call(procCreateBrush, rgb(255, 255, 255))
	app.headerBrush = call(procCreateBrush, rgb(18, 33, 60))
	app.barBrush = call(procCreateBrush, rgb(65, 112, 228))
	app.borderBrush = call(procCreateBrush, rgb(224, 232, 243))
	app.editFont = createFont(-16, false)
	app.labelFont = createFont(-16, true)
	app.headFont = createFont(-30, true)
	app.titleFont = createFont(-16, true)
	app.smallFont = createFont(-14, false)

	app.headBrand = label("C L A D U N   /   LOCALIZACIÓN ES", 34, 21, 670, 24, app.smallFont, 0xd7e5ff)
	app.headTitle = label("Traducir mi ISO", 34, 49, 685, 43, app.headFont, 0xffffff)
	app.headCaption = label("Solo necesitas tu ISO original: no hay que buscar ningún .BPS.", 35, 106, 685, 28, app.editFont, 0xc7d7f1)

	label("01   SELECCIONA LA ISO ORIGINAL (USA)", 52, 180, 610, 24, app.labelFont, 0x152a46)
	app.iso = edit(52, 215)
	app.isoBrowse = button("Examinar", 589, 215, 116, 30, idISO, app.smallFont)
	label("Se verificará la versión exacta de Cladun para PSP (USA).", 52, 255, 632, 20, app.smallFont, 0x677d95)

	label("02   TRADUCCIÓN INTEGRADA", 52, 309, 575, 24, app.labelFont, 0x152a46)
	if automatic.PayloadValid(integratedPatch) {
		label("Parche ES de prueba incorporado · sin descargas adicionales", 52, 340, 640, 23, app.editFont, 0x235d43)
	} else {
		label("Esta compilación NO incluye el parche español experimental.", 52, 340, 645, 23, app.editFont, 0x9f5125)
	}
	label("Salida automática: Cladun-ES-EXPERIMENTAL.iso junto a la ISO original.", 52, 371, 662, 23, app.smallFont, 0x677d95)

	label("Probado el inicio en PPSSPP. Quedan mapas, combates y partidas por comprobar.", 42, 435, 685, 23, app.smallFont, 0x395572)
	label("No se altera ni sobrescribe la ISO original. El resultado se verifica por SHA-256.", 42, 461, 680, 23, app.smallFont, 0x677d95)
	app.status = label("Selecciona tu ISO para comenzar.", 42, 544, 510, 27, app.editFont, 0x395572)
	app.apply = button("Crear ISO de prueba", 533, 509, 179, 43, idApply, app.labelFont)
	call(procEnableWindow, app.apply, 0)
	call(procSetTimer, hwnd, timerID, 125, 0)
}

// OPENFILENAMEW requires a multi-string: display\0pattern\0...\0\0.
// syscall.StringToUTF16 deliberately panics on embedded NUL; that used to
// crash the entire GUI as soon as the user pressed "Examinar".
func isoFilterUTF16() []uint16 {
	return utf16.Encode([]rune("Imagen PSP (*.iso)\x00*.iso\x00Todos los archivos (*.*)\x00*.*\x00\x00"))
}

func chooseFile() string {
	buf := make([]uint16, 32768)
	filter := isoFilterUTF16()
	title := u16("Seleccionar ISO original de Cladun (USA)")
	defExt := u16("iso")
	options := openFileName{
		Owner: app.hwnd, Filter: &filter[0], File: &buf[0], MaxFile: uint32(len(buf)),
		Title:  title,
		Flags:  ofnExplorer | ofnNoChangeDir | ofnPathMustExist | ofnFileMustExist,
		DefExt: defExt,
	}
	options.StructSize = uint32(unsafe.Sizeof(options))
	chosen := call(procGetOpenFile, uintptr(unsafe.Pointer(&options)))
	// The Win32 common dialog retains these pointers for the whole modal call.
	runtime.KeepAlive(filter)
	runtime.KeepAlive(buf)
	runtime.KeepAlive(title)
	runtime.KeepAlive(defExt)
	if chosen == 0 {
		// Cancel is not an error, but failures must not silently vanish.
		if code := call(procCommDlgError); code != 0 {
			showError("No se pudo abrir el explorador", fmt.Sprintf("Windows devolvió el error 0x%04X al abrir el selector de ISO.", code))
		}
		return ""
	}
	return syscall.UTF16ToString(buf)
}

func updateButtonState() {
	app.mu.Lock()
	busy := app.busy
	app.mu.Unlock()
	ready := strings.TrimSpace(getText(app.iso)) != "" && automatic.PayloadValid(integratedPatch)
	value := uintptr(0)
	if ready && !busy {
		value = 1
	}
	call(procEnableWindow, app.apply, value)
	for _, w := range []uintptr{app.isoBrowse, app.iso} {
		v := uintptr(1)
		if busy {
			v = 0
		}
		call(procEnableWindow, w, v)
	}
}

func beginPatch() {
	app.mu.Lock()
	if app.busy {
		app.mu.Unlock()
		return
	}
	app.busy = true
	app.finished = false
	app.phase = "Preparando verificación..."
	app.progress = 0
	app.mu.Unlock()
	iso := getText(app.iso)
	output := automatic.DefaultOutput(iso)
	updateButtonState()
	setText(app.status, "Preparando verificación...")
	go func() {
		info, err := automatic.Apply(iso, output, integratedPatch, func(phase string, done, total uint64) {
			pct := 0
			if total > 0 {
				pct = int(done * 100 / total)
			}
			app.mu.Lock()
			app.phase, app.progress = phase, pct
			app.mu.Unlock()
		})
		app.mu.Lock()
		app.result, app.failure, app.finished, app.busy = info, err, true, false
		app.resultOutput = output
		app.mu.Unlock()
		call(procPostMessage, app.hwnd, wmAppDone, 0, 0)
	}()
}

func drawFill(hdc uintptr, r rect, brush uintptr) {
	call(procFillRect, hdc, uintptr(unsafe.Pointer(&r)), brush)
}
func paint(hwnd uintptr) {
	var ps paintStruct
	hdc := call(procBeginPaint, hwnd, uintptr(unsafe.Pointer(&ps)))
	drawFill(hdc, rect{0, 0, 756, 604}, app.bgBrush)
	drawFill(hdc, rect{0, 0, 756, 145}, app.headerBrush)
	for _, p := range []rect{{32, 164, 720, 281}, {32, 292, 720, 405}} {
		drawFill(hdc, p, app.borderBrush)
		drawFill(hdc, rect{p.L + 1, p.T + 1, p.R - 1, p.B - 1}, app.whiteBrush)
	}
	drawFill(hdc, rect{32, 424, 720, 493}, app.whiteBrush)
	drawFill(hdc, rect{32, 503, 720, 578}, app.whiteBrush)
	drawFill(hdc, rect{42, 524, 523, 532}, app.borderBrush)
	app.mu.Lock()
	pct := app.progress
	app.mu.Unlock()
	if pct > 0 {
		drawFill(hdc, rect{42, 524, 42 + int32(481*pct/100), 532}, app.barBrush)
	}
	call(procEndPaint, hwnd, uintptr(unsafe.Pointer(&ps)))
}

func wndProc(hwnd uintptr, message uint32, wparam, lparam uintptr) uintptr {
	switch message {
	case wmCreate:
		createUI(hwnd)
		return 0
	case wmCommand:
		id := uint16(wparam & 0xffff)
		switch id {
		case idISO:
			if path := chooseFile(); path != "" {
				setText(app.iso, path)
			}
		case idApply:
			beginPatch()
		}
		updateButtonState()
		return 0
	case wmTimer:
		app.mu.Lock()
		phase, pct, busy := app.phase, app.progress, app.busy
		app.mu.Unlock()
		if busy {
			setText(app.status, fmt.Sprintf("%s  ·  %d %%", phase, pct))
			r := rect{42, 525, 537, 533}
			call(procInvalidate, hwnd, uintptr(unsafe.Pointer(&r)), 0)
		}
		return 0
	case wmAppDone:
		app.mu.Lock()
		err, info, done, output := app.failure, app.result, app.finished, app.resultOutput
		app.finished = false
		app.mu.Unlock()
		updateButtonState()
		if done {
			if err != nil {
				setText(app.status, "Verificación detenida: no se generó una ISO válida.")
				showError("No se pudo aplicar el parche", err.Error())
			} else {
				setText(app.status, "Completado: SHA-256 final verificado. Prueba en PPSSPP.")
				showInfo("Parche aplicado", "La ISO experimental se guardó en:\n\n"+output+"\n\nSHA-256:\n"+info.TargetSHA256+"\n\nSe verificaron el arranque y los primeros textos en PPSSPP; no toda la aventura.")
			}
		}
		return 0
	case wmCtlColorStatic:
		hdc, ctrl := wparam, lparam
		if color, ok := app.textHandles[ctrl]; ok {
			call(procSetBkMode, hdc, colorTransparent)
			call(procSetTextColor, hdc, rgb(color>>16&0xff, color>>8&0xff, color&0xff))
			if ctrl == app.headBrand || ctrl == app.headTitle || ctrl == app.headCaption {
				return app.headerBrush
			}
			if ctrl == app.status {
				return app.whiteBrush
			}
			return app.whiteBrush
		}
		return call(procDefWindowProc, hwnd, uintptr(message), wparam, lparam)
	case wmPaint:
		paint(hwnd)
		return 0
	case wmDestroy:
		call(procKillTimer, hwnd, timerID)
		for _, w := range []uintptr{app.editFont, app.headFont, app.titleFont, app.labelFont, app.smallFont, app.bgBrush, app.whiteBrush, app.headerBrush, app.barBrush, app.borderBrush} {
			if w != 0 {
				call(procDeleteObject, w)
			}
		}
		call(procPostQuit, 0)
		return 0
	}
	return call(procDefWindowProc, hwnd, uintptr(message), wparam, lparam)
}
func main() {
	runtime.LockOSThread()
	instance := call(procGetModuleHandle, 0)
	cursor := call(procLoadCursor, 0, 32512)
	icon := call(procLoadIcon, 0, 32512)
	className := u16("CladunPatcherNative")
	c := wndClassEx{
		Size: uint32(unsafe.Sizeof(wndClassEx{})), WndProc: syscall.NewCallback(wndProc),
		Instance: instance, Icon: icon, IconSm: icon, Cursor: cursor,
		ClassName: className,
	}
	if call(procRegisterClass, uintptr(unsafe.Pointer(&c))) == 0 {
		showError("Error de inicio", "No se pudo registrar la ventana de Windows.")
		return
	}
	hwnd := call(procCreateWindow, 0, uintptr(unsafe.Pointer(className)), uintptr(unsafe.Pointer(u16("Cladun · ISO al español (eventos protegidos · experimental) v0.1.4"))), wsOverlappedWindow|wsVisible|wsClipChildren,
		140, 80, 772, 643, 0, 0, instance, 0)
	if hwnd == 0 {
		return
	}
	call(procShowWindow, hwnd, swShow)
	call(procUpdateWindow, hwnd)
	var m msg
	for {
		n := int32(call(procGetMessage, uintptr(unsafe.Pointer(&m)), 0, 0, 0))
		if n <= 0 {
			break
		}
		call(procTranslate, uintptr(unsafe.Pointer(&m)))
		call(procDispatch, uintptr(unsafe.Pointer(&m)))
	}
}
