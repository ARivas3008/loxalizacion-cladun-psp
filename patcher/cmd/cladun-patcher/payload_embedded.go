//go:build cladun_embedded

package main

import _ "embed"

// PRIVATE TEST BUILD ONLY: DO NOT COMMIT OR DISTRIBUTE GAME ASSETS.
//
//go:embed traduccion_es_experimental.bps
var integratedPatch []byte
