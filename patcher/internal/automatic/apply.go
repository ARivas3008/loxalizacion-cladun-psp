// Package automatic applies an independently verified, bundled translation.
// It never asks the player for a patch file and does not modify the original ISO.
package automatic

import (
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"strings"

	"github.com/ARivas3008/loxalizacion-cladun-psp/patcher/internal/bps"
)

// This is a PRIVATE EXPERIMENTAL patch generated from the exact USA ISO.
// The target is a binary candidate, NOT validated for gameplay in PPSSPP.
const PatchSHA256 = "49a2cdf36cb5963a966a29a24da8c5316912c8cd61abebaf8b31b2e42f0c0205"
const TargetSHA256 = "ed9a7a41eec842251f618d292c84cfd0a8c892f1fa31aae7d10d920f3edefb84"

func PayloadValid(patch []byte) bool {
	if len(patch) < 19 || string(patch[:4]) != "BPS1" {
		return false
	}
	h := sha256.Sum256(patch)
	return hex.EncodeToString(h[:]) == PatchSHA256
}

// DefaultOutput always creates a new ISO alongside the original.
func DefaultOutput(iso string) string {
	return filepath.Join(filepath.Dir(iso), "Cladun-ES-EXPERIMENTAL.iso")
}

func samePath(a, b string) bool {
	aa, ea := filepath.Abs(a)
	bb, eb := filepath.Abs(b)
	return ea == nil && eb == nil && strings.EqualFold(filepath.Clean(aa), filepath.Clean(bb))
}

func publishExact(staged, destination string) error {
	// Hard-link is atomic and fails rather than overwriting a destination.
	if err := os.Link(staged, destination); err == nil {
		return nil
	}
	out, err := os.OpenFile(destination, os.O_WRONLY|os.O_EXCL|os.O_CREATE, 0644)
	if err != nil {
		return fmt.Errorf("la salida ya existe o no es accesible: %w", err)
	}
	from, err := os.Open(staged)
	if err != nil {
		out.Close()
		os.Remove(destination)
		return err
	}
	_, err = io.Copy(out, from)
	from.Close()
	if err == nil {
		err = out.Sync()
	}
	if closeErr := out.Close(); err == nil {
		err = closeErr
	}
	if err != nil {
		os.Remove(destination)
	}
	return err
}

func Apply(source, destination string, patch []byte, progress bps.Progress) (bps.Info, error) {
	var zero bps.Info
	if !PayloadValid(patch) {
		return zero, errors.New("esta versión no incluye una traducción experimental verificada")
	}
	if strings.TrimSpace(source) == "" || strings.TrimSpace(destination) == "" || samePath(source, destination) {
		return zero, errors.New("las rutas de entrada y salida deben ser distintas")
	}
	if _, err := os.Lstat(destination); err == nil {
		return zero, errors.New("la ISO de salida ya existe: no se sobrescribirá")
	} else if !os.IsNotExist(err) {
		return zero, err
	}
	// BPS is extracted to a private temporary file solely for the generic,
	// independently unit-tested BPS engine. It is deleted after application.
	patchFile, err := os.CreateTemp("", "cladun-integrado-*.bps")
	if err != nil {
		return zero, err
	}
	patchPath := patchFile.Name()
	defer os.Remove(patchPath)
	if _, err = patchFile.Write(patch); err != nil {
		patchFile.Close()
		return zero, err
	}
	if err = patchFile.Close(); err != nil {
		return zero, err
	}

	// BPS staging must be a name that does not yet exist. It resides in the
	// output directory so verified publication can use an atomic hard link.
	trialFile, err := os.CreateTemp(filepath.Dir(destination), ".cladun-validando-*.iso")
	if err != nil {
		return zero, err
	}
	trialPath := trialFile.Name()
	trialFile.Close()
	os.Remove(trialPath)
	defer os.Remove(trialPath)
	info, err := bps.Apply(source, patchPath, trialPath, progress)
	if err != nil {
		return zero, err
	}
	if info.TargetSHA256 != TargetSHA256 {
		return zero, errors.New("la ISO candidata no coincide con el SHA-256 auditado; resultado descartado")
	}
	if err := publishExact(trialPath, destination); err != nil {
		return zero, err
	}
	return info, nil
}
