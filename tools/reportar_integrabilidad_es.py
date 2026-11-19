#!/usr/bin/env python3
"""Inventario de textos técnicamente integrables por el inyector experimental.

No escribe ISO. No confunde planificación con validación PPSSPP.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
from integrar_parche_seguro import source_rows, plan_rows, SOURCE, DRAFT

def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--original", type=Path, default=SOURCE)
    cli.add_argument("--borrador", type=Path, default=DRAFT)
    cli.add_argument("--reporte", type=Path)
    args = cli.parse_args()
    changes, blocked, identical = plan_rows(source_rows(args.original, args.borrador))
    counts = {key: len(value) for key, value in sorted(changes.items())}
    result = {
        "estado": "PREVISION_ESTATICA_NO_CERTIFICA_INSERCION_NI_PPSSPP",
        "total": 9237,
        "textos_con_plan_de_integracion_experimental": sum(counts.values()),
        "sin_cambios_binarios_necesarios": identical,
        "pendientes": len(blocked),
        "candidatos_por_origen": counts,
        "bloqueos_por_motivo": dict(sorted(Counter(x["motivo"] for x in blocked).items())),
        "rutas_textuales_reconstruidas": ["SCRIPT.SDT/SCRIPT.DAT", "DATABASE.DAT/STRTBL.DAT",
                                         "DATABASE.DAT/*_campos_fijos", "STAFFROLL.TXT", "SYS.DAT2/6_png_textuales"],
        "recursos_no_textuales_permitidos": 0,
        "cobertura_preparacion_100_pct": len(blocked) == 0 and sum(counts.values()) + identical == 9237,
        "aprobados_insercion_final": 0,
        "verificado_en_ppsspp": False
    }
    output = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    print(output)
    if args.reporte:
        args.reporte.parent.mkdir(parents=True, exist_ok=True)
        args.reporte.write_text(output, encoding="utf-8")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
