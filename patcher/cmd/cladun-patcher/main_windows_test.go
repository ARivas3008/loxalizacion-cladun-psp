//go:build windows

package main

import (
	"reflect"
	"testing"
	"unicode/utf16"
	"unsafe"
)

func TestISOFilterUTF16Win32Multistring(t *testing.T) {
	got := isoFilterUTF16()
	want := utf16.Encode([]rune("Imagen PSP (*.iso)\x00*.iso\x00Todos los archivos (*.*)\x00*.*\x00\x00"))
	if !reflect.DeepEqual(got, want) {
		t.Fatalf("incorrect Win32 dialog filter: %v", got)
	}
	if len(got) < 2 || got[len(got)-2] != 0 || got[len(got)-1] != 0 {
		t.Fatal("Win32 dialog filter must terminate with two NUL units")
	}
}

func TestOpenFileNameWin64Size(t *testing.T) {
	if unsafe.Sizeof(uintptr(0)) == 8 && unsafe.Sizeof(openFileName{}) != 152 {
		t.Fatalf("OPENFILENAMEW must be 152 bytes on 64-bit Windows; got %d", unsafe.Sizeof(openFileName{}))
	}
}
