#!/usr/bin/env python3
"""F2: X11 screenshot / PPSSPP PID / real-ISO fd corroboration (not WS or GE).

PRIVATE screenshots only. X11 is NOT the PSP framebuffer. _NET_WM_PID is a
client-supplied X11 property: it corroborates, does not prove loaded ISO.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
try:
    from tools.f2_iso_proceso_ppsspp import validate_iso,proc_snapshot,paired_observations,SOURCE_SHA,PROBE_SHA
except ModuleNotFoundError:
    from f2_iso_proceso_ppsspp import validate_iso,proc_snapshot,paired_observations,SOURCE_SHA,PROBE_SHA

def verify_window_metadata(expected_pid:int,reported_pid:int,name:str,width:int,height:int,x:int,y:int):
    if reported_pid!=expected_pid or not isinstance(reported_pid,int) or expected_pid<=0:
        raise ValueError('X11 _NET_WM_PID no coincide con PPSSPP')
    if not isinstance(name,str) or 'CLADUN' not in name.upper() or not ('PPSSPP' in name.upper() or 'NPUH' in name.upper()):
        raise ValueError('Nombre de ventana X11 incompatible con Cladun')
    if (width,height)!=(960,544):
        raise ValueError('La ventana X11 debe ser 960x544; no confundir con framebuffer PSP')
    if x<0 or y<0:raise ValueError('Ventana fuera del origen X11')
    return {'x':x,'y':y,'width':width,'height':height,'window_pid':reported_pid,
            'window_title_is_cladun':True,'window_size_960x544':True}

def find_window(xdisplay:str,pid:int):
    from Xlib import X,display
    con=display.Display(xdisplay)
    try:
        root=con.screen().root
        atom=con.intern_atom('_NET_WM_PID',only_if_exists=True)
        if not atom:raise ValueError('Falta X11 _NET_WM_PID')
        for win in root.query_tree().children:
            try:
                prop=win.get_full_property(atom,X.AnyPropertyType)
                if not prop or len(prop.value)!=1 or int(prop.value[0])!=pid:continue
                geo=win.get_geometry()
                loc=root.translate_coords(win,0,0)
                info=verify_window_metadata(pid,int(prop.value[0]),str(win.get_wm_name() or ''),
                                             geo.width,geo.height,loc.x,loc.y)
                info['window_id_hex']=hex(win.id)
                return info
            except (ValueError,TypeError):continue
        raise ValueError('No existe ventana de Cladun vinculada al PID y 960x544')
    finally:con.close()

def checked_output(path:Path,repo:Path):
    path=Path(path)
    dest=path.expanduser().resolve(strict=False)
    root=repo.resolve()
    if path.suffix.lower()!='.png' or dest==root or root in dest.parents:
        raise ValueError('PNG comercial solo fuera del repositorio')
    if dest.exists():raise FileExistsError('No sobrescribir evidencia')
    dest.parent.mkdir(parents=True,exist_ok=True)
    return dest

def capture(xdisplay:str,pid:int,iso:Path,role:str,path:Path,repo:Path):
    from PIL import ImageGrab
    approved={'usa':SOURCE_SHA,'sonda':PROBE_SHA,'f1':F1_SHA}
    if role not in approved:raise ValueError('Tipo ISO desconocido')
    expect=approved[role]
    iso_first=validate_iso(iso,expect)
    first=proc_snapshot(pid,iso)
    window=find_window(xdisplay,pid)
    out=checked_output(path,repo)
    box=(window['x'],window['y'],window['x']+window['width'],window['y']+window['height'])
    screen=ImageGrab.grab(bbox=box,xdisplay=xdisplay).convert('RGB')
    if screen.size!=(960,544):raise ValueError('Frame X11 de tamaño inesperado')
    screen.save(out,format='PNG')
    second_window=find_window(xdisplay,pid)
    last=proc_snapshot(pid,iso)
    iso_last=validate_iso(iso,expect)
    if second_window!=window:
        out.unlink();raise ValueError('La ventana cambió durante la captura')
    if (iso_first['inode'],iso_first['device'])!=(iso_last['inode'],iso_last['device']):
        out.unlink();raise ValueError('La ISO cambió de inode')
    paired=paired_observations(first,last)
    if not paired['pid_starttime_stable']:
        out.unlink();raise ValueError('PID reciclado')
    picture=out.read_bytes()
    return {'schema':'cladun.f2.x11_pid_procfs_evidence.v1',
       'runtime':'REAL_X11_PPSSPP_1.20.4',
       'source_iso_role':role,'source_iso_sha256':iso_first['source_iso_sha256'],
       'x11':window,'x11_window_pid_correlated_to_procfs':True,
       'procfs_before':first,'procfs_after':last,'paired':paired,
       'screenshot_x11':{'filename':out.name,'sha256':hashlib.sha256(picture).hexdigest(),
                         'bytes':len(picture),'width':960,'height':544},
       'this_is_psp_framebuffer':False,'websocket_server_pid_correlated':False,
       'runtime_loaded_iso_identity_proven':False,'mips_ram_ge_vram_proven':False,
       'warning':'El PID X11 y el ISO abierto corroboran acceso, no GE ni qué ISO está dibujando el motor.'}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--display',default=':95')
    p.add_argument('--pid',type=int,required=True)
    p.add_argument('--iso',type=Path,required=True)
    p.add_argument('--tipo',choices=('usa','sonda','f1'),required=True)
    p.add_argument('--png-privado',type=Path,required=True)
    p.add_argument('--manifiesto-privado',type=Path,required=True)
    a=p.parse_args()
    root=Path(__file__).resolve().parents[1]
    report=capture(a.display,a.pid,a.iso,a.tipo,a.png_privado,root)
    target=a.manifiesto_privado.expanduser().resolve(strict=False)
    if target.exists() or target.suffix!='.json' or target==root or root in target.parents:
        raise ValueError('Manifiesto privado nuevo fuera del checkout')
    with target.open('x',encoding='utf-8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
    print(json.dumps({'png_sha256':report['screenshot_x11']['sha256'],
        'x11_pid_match':True,
        'iso_open_in_pid':report['paired']['same_inode_open_before_and_after'],
        'is_tuika_scene_proven':False},ensure_ascii=False))

if __name__=='__main__':main()
