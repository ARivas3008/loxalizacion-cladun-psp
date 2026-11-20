package automatic

import (
	"os"
	"path/filepath"
	"testing"
)

func TestAbsentPayloadFailsClosed(t *testing.T) {
	if PayloadValid(nil) || PayloadValid([]byte("BPS1not-a-real-patch")) {
		t.Fatal("invalid payload accepted")
	}
	dir := t.TempDir()
	out := filepath.Join(dir, "target.iso")
	if _, err := Apply(filepath.Join(dir, "source.iso"), out, nil, nil); err == nil {
		t.Fatal("missing payload accepted")
	}
	if _, err := os.Stat(out); !os.IsNotExist(err) {
		t.Fatalf("unexpected output: %v", err)
	}
}
func TestOutputSelection(t *testing.T) {
	got := DefaultOutput(filepath.Join("input", "game.iso"))
	want := filepath.Join("input", "Cladun-ES-EXPERIMENTAL.iso")
	if got != want {
		t.Fatalf("%q != %q", got, want)
	}
}
func TestNeverOverwrite(t *testing.T) {
	d := t.TempDir()
	f := filepath.Join(d, "src.iso")
	if err := os.WriteFile(f, []byte("sample"), 0644); err != nil {
		t.Fatal(err)
	}
	if _, err := Apply(f, f, []byte("bad"), nil); err == nil {
		t.Fatal("same path not rejected")
	}
}
