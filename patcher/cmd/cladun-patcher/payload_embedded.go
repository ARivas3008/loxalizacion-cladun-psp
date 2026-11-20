//go:build cladun_embedded

package main

import _ "embed"

// Experimental user patch: differential BPS only, no ISO.
// The included payload is integrity checked by automatic.PayloadValid.
//
//go:embed traduccion_es_experimental.bps
var integratedPatch []byte
