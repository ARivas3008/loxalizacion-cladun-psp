#!/usr/bin/env python3
"""Extracción → auditoría de campos → corpus y lectura en TXT → QA.

Requiere Python 3.10+ y una copia propia de la ISO de PSP. Sin paquetes externos.
"""
from __future__ import annotations
import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

HERE=Path(__file__).resolve().parent

def run(*args: str) -> None:
    print('Ejecutando:',*args,flush=True)
    subprocess.run([sys.executable,*args],check=True)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--iso',type=Path,required=True)
    ap.add_argument('--salida',type=Path,default=HERE.parent)
    args=ap.parse_args()
    iso=args.iso.resolve(strict=True)
    out=args.salida.resolve()
    with tempfile.TemporaryDirectory(prefix='cladun_raw_') as tmp:
        tmp=Path(tmp)
        run(str(HERE/'extract_cladun.py'),str(iso),'-o',str(tmp))
        run(str(HERE/'revisar_corpus.py'),'--iso',str(iso),'--raw',str(tmp/'corpus/todo_el_texto.csv'),'--salida',str(out))
    run(str(HERE/'verificar_integridad.py'),'--raiz',str(out),'--guardar')
    print('Corpus y TXT originales generados. No se ha traducido ningún texto.')

if __name__=='__main__': main()
