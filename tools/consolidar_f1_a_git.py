#!/usr/bin/env python3
"""Una única transacción Git de F1 literaria: CSV, ambos TXT, bitácora, vistas.

Se llama en GitHub Actions antes de git add/commit. Nunca modifica binarios.
Deja intactos fuente original, ID, offset y registros ajenos.
"""
from __future__ import annotations
import csv, subprocess, sys, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DRAFT = ROOT/"traduccion/CLADUN_BORRADOR_ES.csv"
EXPECT = {"005710": ("          EN", "          Sí"),
          "005713": ("         APAGADO", "         No")}
def main():
    with DRAFT.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        columns = reader.fieldnames
        rows = list(reader)
    if len(rows) != 9237: raise ValueError("corpus incompleto")
    found=set()
    for row in rows:
        gid=row["grupo_id"]
        if gid not in EXPECT:continue
        original,new=EXPECT[gid]
        if gid in found or row["espanol"] != original:
            raise ValueError(f"F1 preimagen desconocida o duplicada: {gid}")
        row["espanol"]=new;found.add(gid)
    if found != set(EXPECT):raise ValueError("IDs ON/OFF ausentes")
    with tempfile.TemporaryDirectory(prefix="cladun_f1_editor_") as td:
        candidate=Path(td)/"editor.csv"
        with candidate.open("w", encoding="utf-8-sig", newline="") as f:
            w=csv.DictWriter(f, fieldnames=columns);w.writeheader();w.writerows(rows)
        subprocess.run([sys.executable, "tools/aplicar_correcciones_editor.py",
                        "--entrada",str(candidate),"--raiz",str(ROOT),"--aplicar",
                        "--editor","f1_ppsspp_visual_2026_11_21"],cwd=ROOT,check=True)
    with DRAFT.open(encoding="utf-8-sig",newline="") as f:
        final={row["grupo_id"]:row["espanol"] for row in csv.DictReader(f)}
    for gid, (_old,new) in EXPECT.items():
        if final.get(gid)!=new:raise ValueError("Sync falló "+gid)
    print("F1 LITERARIA SINCRONIZADA: 2 registros, 2 TXT, bitácora, vistas")
if __name__=="__main__": main()
