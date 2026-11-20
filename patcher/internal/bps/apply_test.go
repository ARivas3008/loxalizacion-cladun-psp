package bps

import (
	"bufio"
	"bytes"
	"crypto/sha256"
	"encoding/binary"
	"encoding/hex"
	"hash/crc32"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func encodeNumber(v uint64) []byte {
	var out []byte
	for {
		b := byte(v & 127)
		v >>= 7
		if v == 0 {
			return append(out, b|128)
		}
		out = append(out, b)
		v--
	}
}
func signedOffset(n int64) []byte {
	if n >= 0 {
		return encodeNumber(uint64(n) << 1)
	}
	return encodeNumber((uint64(-n) << 1) | 1)
}
func encAction(action, n uint64) []byte { return encodeNumber((n-1)<<2 | action) }
func buildPatch(src, dst []byte, commands []byte) []byte {
	var p []byte
	p = append(p, []byte("BPS1")...)
	p = append(p, encodeNumber(uint64(len(src)))...)
	p = append(p, encodeNumber(uint64(len(dst)))...)
	p = append(p, encodeNumber(0)...)
	p = append(p, commands...)
	var f [4]byte
	binary.LittleEndian.PutUint32(f[:], crc32.ChecksumIEEE(src))
	p = append(p, f[:]...)
	binary.LittleEndian.PutUint32(f[:], crc32.ChecksumIEEE(dst))
	p = append(p, f[:]...)
	binary.LittleEndian.PutUint32(f[:], crc32.ChecksumIEEE(p))
	p = append(p, f[:]...)
	return p
}
func TestReadNumber(t *testing.T) {
	for _, n := range []uint64{0, 1, 127, 128, 129, 255, 123456, 1 << 35, 1 << 61} {
		got, err := readNumber(bufio.NewReader(bytes.NewBuffer(encodeNumber(n))))
		if err != nil || got != n {
			t.Fatalf("n=%d got=%d err=%v", n, got, err)
		}
	}
}

// readNumber expects a buffered reader; helper keeps the test readable.
func TestAllBPSActions(t *testing.T) {
	src := []byte("0123456789abcdefghij")
	dst := []byte("0123HEY789abababab!")
	commands := []byte{}
	commands = append(commands, encAction(0, 4)...) // SourceRead -> 0123
	commands = append(commands, encAction(1, 3)...) // TargetRead -> HEY
	commands = append(commands, []byte("HEY")...)
	commands = append(commands, encAction(2, 3)...) // SourceCopy source offset +7 -> 789
	commands = append(commands, signedOffset(7)...)
	commands = append(commands, encAction(1, 2)...) // TargetRead -> ab
	commands = append(commands, []byte("ab")...)
	commands = append(commands, encAction(3, 6)...) // TargetCopy from target offset 10
	commands = append(commands, signedOffset(10)...)
	commands = append(commands, encAction(1, 1)...) // TargetRead -> !
	commands = append(commands, '!')
	tmp := t.TempDir()
	source := filepath.Join(tmp, "src.iso")
	patch := filepath.Join(tmp, "test.bps")
	output := filepath.Join(tmp, "out.iso")
	if err := os.WriteFile(source, src, 0644); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(patch, buildPatch(src, dst, commands), 0644); err != nil {
		t.Fatal(err)
	}
	hash := sha256.Sum256(src)
	info, err := applyWithExpectedSource(source, patch, output, hex.EncodeToString(hash[:]), nil)
	if err != nil {
		t.Fatal(err)
	}
	out, err := os.ReadFile(output)
	if err != nil {
		t.Fatal(err)
	}
	if !bytes.Equal(dst, out) {
		t.Fatalf("want %q got %q", dst, out)
	}
	if info.TargetSHA256 == "" {
		t.Fatal("missing SHA-256")
	}
	// An existing target must never be overwritten.
	if _, err = applyWithExpectedSource(source, patch, output, hex.EncodeToString(hash[:]), nil); err == nil {
		t.Fatal("allowed overwrite")
	}
}
func TestCorruptBPSRejectedWithoutOutput(t *testing.T) {
	src := []byte("testing")
	commands := append(encAction(0, uint64(len(src))), []byte{}...)
	p := buildPatch(src, src, commands)
	p[5] ^= 1
	tmp := t.TempDir()
	orig := filepath.Join(tmp, "in.iso")
	patch := filepath.Join(tmp, "bad.bps")
	out := filepath.Join(tmp, "out.iso")
	os.WriteFile(orig, src, 0644)
	os.WriteFile(patch, p, 0644)
	sha := sha256.Sum256(src)
	_, err := applyWithExpectedSource(orig, patch, out, hex.EncodeToString(sha[:]), nil)
	if err == nil || !strings.Contains(err.Error(), "CRC32") {
		t.Fatalf("unexpected error: %v", err)
	}
	if _, err = os.Stat(out); !os.IsNotExist(err) {
		t.Fatalf("output created: %v", err)
	}
}
func TestSourceHashMustMatch(t *testing.T) {
	tmp := t.TempDir()
	src := filepath.Join(tmp, "iso")
	patch := filepath.Join(tmp, "patch")
	out := filepath.Join(tmp, "out")
	os.WriteFile(src, []byte("one"), 0644)
	os.WriteFile(patch, []byte("BPS1"), 0644)
	_, err := applyWithExpectedSource(src, patch, out, strings.Repeat("0", 64), nil)
	if err == nil || !strings.Contains(err.Error(), "SHA-256") {
		t.Fatalf("unexpected: %v", err)
	}
}
