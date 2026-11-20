//go:build !cladun_embedded

package main

// Public source compiles without bundling an unapproved experimental patch.
// The interface refuses to create an ISO until an audited payload is embedded.
var integratedPatch []byte
