// Package bps applies BPS1 deltas without loading the input ISO into memory.
// The source image is always read-only; output is staged and never overwrites a file.
package bps

import (
	"bufio"
	"crypto/sha256"
	"encoding/binary"
	"encoding/hex"
	"errors"
	"fmt"
	"hash/crc32"
	"io"
	"os"
	"path/filepath"
	"strings"
)

// The only ISO revision tested by the localization repository.
const SourceSHA256 = "b73b263fce863e51a0e27d0d11d6bde2886e439a18e2bb186d497619a1b79f"
const MaxTargetSize uint64 = 8 << 30 // guard against corrupt or hostile headers
const copyBuffer = 64 << 10

// Info contains the independent format-level checks performed while applying.
type Info struct {
	SourceSHA256 string
	TargetSHA256 string
	SourceCRC32  uint32
	TargetCRC32  uint32
	PatchCRC32   uint32
	SourceSize   uint64
	TargetSize   uint64
}

// Progress is always invoked from the worker goroutine, not the UI thread.
type Progress func(phase string, done, total uint64)

func report(cb Progress, phase string, done, total uint64) {
	if cb != nil {
		cb(phase, done, total)
	}
}

func fileDigest(path string, cb Progress, phase string) (string, uint32, uint64, error) {
	f, err := os.Open(path)
	if err != nil {
		return "", 0, 0, err
	}
	defer f.Close()
	st, err := f.Stat()
	if err != nil {
		return "", 0, 0, err
	}
	total := uint64(st.Size())
	sha := sha256.New()
	crc := crc32.NewIEEE()
	mw := io.MultiWriter(sha, crc)
	buf := make([]byte, 1<<20)
	var done uint64
	report(cb, phase, 0, total)
	for {
		n, er := f.Read(buf)
		if n > 0 {
			if _, err = mw.Write(buf[:n]); err != nil {
				return "", 0, 0, err
			}
			done += uint64(n)
			if done == total || done%(16<<20) < uint64(n) {
				report(cb, phase, done, total)
			}
		}
		if er == io.EOF {
			break
		}
		if er != nil {
			return "", 0, 0, er
		}
	}
	return hex.EncodeToString(sha.Sum(nil)), crc.Sum32(), done, nil
}

func readNumber(r *bufio.Reader) (uint64, error) {
	var value uint64
	shift := uint64(1)
	for i := 0; i < 11; i++ {
		b, err := r.ReadByte()
		if err != nil {
			return 0, fmt.Errorf("cabecera BPS truncada: %w", err)
		}
		n := uint64(b & 0x7f)
		if n != 0 && shift > (^uint64(0)-value)/n {
			return 0, errors.New("entero BPS desbordado")
		}
		value += n * shift
		if b&0x80 != 0 {
			return value, nil
		}
		if shift > (^uint64(0) >> 7) {
			return 0, errors.New("entero BPS fuera de rango")
		}
		shift <<= 7
		if value > ^uint64(0)-shift {
			return 0, errors.New("entero BPS fuera de rango")
		}
		value += shift
	}
	return 0, errors.New("entero BPS excesivamente largo")
}

func addSignedOffset(current int64, encoded uint64) (int64, error) {
	mag := encoded >> 1
	if mag > uint64(^uint64(0)>>1) {
		return 0, errors.New("desplazamiento BPS inválido")
	}
	delta := int64(mag)
	if encoded&1 != 0 {
		delta = -delta
	}
	next := current + delta
	if (delta > 0 && next < current) || (delta < 0 && next > current) || next < 0 {
		return 0, errors.New("desplazamiento BPS fuera de rango")
	}
	return next, nil
}

func copyFromFile(dst io.Writer, src io.ReaderAt, at int64, n int64, buf []byte) error {
	for n > 0 {
		take := int64(len(buf))
		if n < take {
			take = n
		}
		got, err := src.ReadAt(buf[:int(take)], at)
		if err != nil && !(err == io.EOF && int64(got) == take) {
			return fmt.Errorf("lectura BPS fuera del origen: %w", err)
		}
		if int64(got) != take {
			return errors.New("lectura BPS incompleta")
		}
		w, err := dst.Write(buf[:got])
		if err != nil {
			return err
		}
		if w != got {
			return io.ErrShortWrite
		}
		n -= take
		at += take
	}
	return nil
}

// Apply reads a user-owned ISO and BPS1 file, checks the complete source SHA-256,
// BPS patch CRC32, source CRC32 and output CRC32, then installs the output with
// create-if-absent semantics. It supports all four standard BPS actions.
func Apply(source, patch, output string, cb Progress) (Info, error) {
	return applyWithExpectedSource(source, patch, output, SourceSHA256, cb)
}

func applyWithExpectedSource(source, patch, output, expectedSHA string, cb Progress) (Info, error) {
	var info Info
	paths := []string{source, patch, output}
	canon := make([]string, len(paths))
	for i, p := range paths {
		if strings.TrimSpace(p) == "" {
			return info, errors.New("selecciona los tres archivos")
		}
		a, err := filepath.Abs(p)
		if err != nil {
			return info, err
		}
		canon[i] = filepath.Clean(a)
	}
	for i := 0; i < len(canon); i++ {
		for j := i + 1; j < len(canon); j++ {
			if strings.EqualFold(canon[i], canon[j]) {
				return info, errors.New("la ISO, el parche y la salida deben ser archivos diferentes")
			}
		}
	}
	// Symlinks may point to another of the chosen paths.
	for i := 0; i < 2; i++ {
		real, err := filepath.EvalSymlinks(canon[i])
		if err != nil {
			return info, err
		}
		canon[i] = real
	}
	if _, err := os.Lstat(canon[2]); err == nil {
		return info, errors.New("el archivo de salida ya existe; no se sobrescribirá")
	} else if !os.IsNotExist(err) {
		return info, err
	}
	if strings.EqualFold(canon[0], canon[1]) || strings.EqualFold(canon[0], canon[2]) || strings.EqualFold(canon[1], canon[2]) {
		return info, errors.New("rutas duplicadas")
	}
	sourceSHA, sourceCRC, actualSize, err := fileDigest(canon[0], cb, "Verificando ISO original")
	if err != nil {
		return info, err
	}
	if sourceSHA != expectedSHA {
		return info, errors.New("la ISO no coincide con la edición USA auditada (SHA-256 distinto)")
	}
	info.SourceSHA256, info.SourceCRC32 = sourceSHA, sourceCRC

	pf, err := os.Open(canon[1])
	if err != nil {
		return info, err
	}
	defer pf.Close()
	pst, err := pf.Stat()
	if err != nil {
		return info, err
	}
	if pst.Size() < 19 {
		return info, errors.New("archivo BPS demasiado pequeño")
	}
	patchLength := pst.Size()
	var footer [12]byte
	if _, err = pf.ReadAt(footer[:], patchLength-12); err != nil {
		return info, err
	}
	wantSourceCRC := binary.LittleEndian.Uint32(footer[0:4])
	info.TargetCRC32 = binary.LittleEndian.Uint32(footer[4:8])
	info.PatchCRC32 = binary.LittleEndian.Uint32(footer[8:12])
	if wantSourceCRC != sourceCRC {
		return info, errors.New("el CRC del origen no coincide con el parche BPS")
	}
	// CRC32 of the entire BPS file except its last four checksum bytes.
	h := crc32.NewIEEE()
	section := io.NewSectionReader(pf, 0, patchLength-4)
	var scanned int64
	chkbuf := make([]byte, 1<<20)
	report(cb, "Validando integridad del parche", 0, uint64(patchLength-4))
	for {
		n, er := section.Read(chkbuf)
		if n > 0 {
			if _, err = h.Write(chkbuf[:n]); err != nil {
				return info, err
			}
			scanned += int64(n)
			if scanned == patchLength-4 || scanned%(16<<20) < int64(n) {
				report(cb, "Validando integridad del parche", uint64(scanned), uint64(patchLength-4))
			}
		}
		if er == io.EOF {
			break
		}
		if er != nil {
			return info, er
		}
	}
	if h.Sum32() != info.PatchCRC32 {
		return info, errors.New("el parche BPS está corrupto (CRC32 incorrecto)")
	}

	r := bufio.NewReaderSize(io.NewSectionReader(pf, 0, patchLength-12), copyBuffer)
	var magic [4]byte
	if _, err = io.ReadFull(r, magic[:]); err != nil {
		return info, err
	}
	if string(magic[:]) != "BPS1" {
		return info, errors.New("el archivo seleccionado no es BPS1")
	}
	srcLen, err := readNumber(r)
	if err != nil {
		return info, err
	}
	dstLen, err := readNumber(r)
	if err != nil {
		return info, err
	}
	metaLen, err := readNumber(r)
	if err != nil {
		return info, err
	}
	info.SourceSize, info.TargetSize = srcLen, dstLen
	if srcLen != actualSize {
		return info, errors.New("el tamaño de la ISO original no coincide con el parche")
	}
	if dstLen == 0 || dstLen > MaxTargetSize {
		return info, errors.New("tamaño objetivo BPS no permitido")
	}
	// Important: metadata also obeys the footer-bound reader.
	if metaLen > uint64(patchLength-12) {
		return info, errors.New("metadatos BPS demasiado grandes")
	}
	if _, err = io.CopyN(io.Discard, r, int64(metaLen)); err != nil {
		return info, errors.New("metadatos BPS truncados")
	}

	orig, err := os.Open(canon[0])
	if err != nil {
		return info, err
	}
	defer orig.Close()
	dir := filepath.Dir(canon[2])
	temp, err := os.CreateTemp(dir, ".cladun-*.partial")
	if err != nil {
		return info, err
	}
	tempPath := temp.Name()
	defer os.Remove(tempPath)
	defer temp.Close()
	scratch := make([]byte, copyBuffer)
	var written uint64
	var srcRel, tgtRel int64
	report(cb, "Aplicando traducción", 0, dstLen)
	for written < dstLen {
		inst, er := readNumber(r)
		if er != nil {
			return info, fmt.Errorf("comando BPS incompleto: %w", er)
		}
		action := inst & 3
		count := (inst >> 2) + 1
		if count > dstLen-written || count > uint64(^uint64(0)>>1) {
			return info, errors.New("comando BPS excede el tamaño objetivo")
		}
		n := int64(count)
		switch action {
		case 0: // SourceRead at output position.
			if written+count > srcLen {
				return info, errors.New("SourceRead fuera del archivo original")
			}
			err = copyFromFile(temp, orig, int64(written), n, scratch)
		case 1: // TargetRead from literal patch bytes.
			var copied int64
			copied, err = io.CopyN(temp, r, n)
			if err == nil && copied != n {
				err = io.ErrUnexpectedEOF
			}
		case 2: // SourceCopy with relative signed seek.
			var offset uint64
			offset, err = readNumber(r)
			if err != nil {
				break
			}
			srcRel, err = addSignedOffset(srcRel, offset)
			if err != nil {
				break
			}
			if uint64(srcRel) > srcLen || count > srcLen-uint64(srcRel) {
				err = errors.New("SourceCopy fuera del archivo original")
				break
			}
			err = copyFromFile(temp, orig, srcRel, n, scratch)
			srcRel += n
		case 3: // TargetCopy; overlapping back-references are legal in BPS1.
			var offset uint64
			offset, err = readNumber(r)
			if err != nil {
				break
			}
			tgtRel, err = addSignedOffset(tgtRel, offset)
			if err != nil {
				break
			}
			if tgtRel >= int64(written) {
				err = errors.New("TargetCopy apunta a bytes no escritos")
				break
			}
			remain := n
			distance := int64(written) - tgtRel
			for remain > 0 {
				take := int64(len(scratch))
				if take > remain {
					take = remain
				}
				initial := take
				if initial > distance {
					initial = distance
				}
				var got int
				got, err = temp.ReadAt(scratch[:int(initial)], tgtRel)
				if err != nil {
					break
				}
				if int64(got) != initial {
					err = io.ErrUnexpectedEOF
					break
				}
				// Reproduce overlapping BPS copies without one syscall per byte.
				for i := initial; i < take; i++ {
					scratch[int(i)] = scratch[int(i-distance)]
				}
				var put int
				put, err = temp.Write(scratch[:int(take)])
				if err != nil || int64(put) != take {
					if err == nil {
						err = io.ErrShortWrite
					}
					break
				}
				tgtRel += take
				written += uint64(take)
				remain -= take
			}
			if err != nil {
				break
			}
			// TargetCopy already updates written in its loop.
			report(cb, "Aplicando traducción", written, dstLen)
			continue
		}
		if err != nil {
			return info, err
		}
		written += count
		if written == dstLen || written%(16<<20) < count {
			report(cb, "Aplicando traducción", written, dstLen)
		}
	}
	if _, err = r.ReadByte(); err != io.EOF {
		if err == nil {
			return info, errors.New("el parche contiene instrucciones sobrantes")
		}
		return info, err
	}
	if err = temp.Sync(); err != nil {
		return info, err
	}
	targetSHA, targetCRC, finalSize, err := fileDigest(tempPath, cb, "Verificando ISO traducida")
	if err != nil {
		return info, err
	}
	if finalSize != dstLen || targetCRC != info.TargetCRC32 {
		return info, errors.New("la ISO generada no coincide con el CRC32 objetivo")
	}
	info.TargetSHA256 = targetSHA
	if err = temp.Close(); err != nil {
		return info, err
	}
	// Hard-link is atomic and fails if the target already exists. On file systems
	// where hard-links are unavailable, use O_EXCL and copy (never overwrite).
	if err = os.Link(tempPath, canon[2]); err != nil {
		out, er := os.OpenFile(canon[2], os.O_WRONLY|os.O_CREATE|os.O_EXCL, 0644)
		if er != nil {
			return info, fmt.Errorf("no se pudo publicar la salida sin sobrescribir: %w", er)
		}
		from, er := os.Open(tempPath)
		if er != nil {
			out.Close()
			os.Remove(canon[2])
			return info, er
		}
		_, er = io.Copy(out, from)
		from.Close()
		if er == nil {
			er = out.Sync()
		}
		if cerr := out.Close(); er == nil {
			er = cerr
		}
		if er != nil {
			os.Remove(canon[2])
			return info, er
		}
	}
	report(cb, "Completado", dstLen, dstLen)
	return info, nil
}
