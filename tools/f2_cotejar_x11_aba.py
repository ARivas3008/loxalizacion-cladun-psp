#!/usr/bin/env python3
"""F2: control temporal X11 A/B/A (original/sonda/original), solo métricas.

El cotejo de píxeles NO certifica sincronización de escena, origen TUIKA,
identidad del ISO cargado, framebuffer PSP ni MIPS/RAM/GE/VRAM. No exporta PNG.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from PIL import Image
try:
    import tools.f2_cotejar_x11_tuika as x11
except ModuleNotFoundError:
    import f2_cotejar_x11_tuika as x11

def magenta(color):
    return color[0]>=230 and color[1]<=45 and color[2]>=220

def metrics(original_before:Image.Image, probe:Image.Image, original_after:Image.Image)->dict:
    images=(original_before,probe,original_after)
    if any(im.mode!='RGB' for im in images) or len({im.size for im in images})!=1:
        raise ValueError('A/B/A requires three RGB images of identical size')
    w,h=original_before.size
    if not 1<=w*h<=4096*4096:
        raise ValueError('Dimensions outside bounds')
    stable=unstable=changed=magenta_candidate=native_magenta=ambiguous=0
    box_changed=box_magenta=None
    def include(box,x,y):
        return [x,y,x,y] if box is None else [min(box[0],x),min(box[1],y),max(box[2],x),max(box[3],y)]
    for n,(a,b,c) in enumerate(zip(original_before.getdata(),probe.getdata(),original_after.getdata())):
        if a==c:
            stable+=1
            if magenta(a):native_magenta+=1
            if a!=b:
                changed+=1
                box_changed=include(box_changed,n%w,n//w)
                if not magenta(a) and magenta(b):
                    magenta_candidate+=1
                    box_magenta=include(box_magenta,n%w,n//w)
        else:
            unstable+=1
            if b!=a or b!=c:ambiguous+=1
    if stable+unstable!=w*h:raise AssertionError('Incomplete pixel partition')
    return {
        'dimensions_px':[w,h],'total_pixels':w*h,
        'stable_usa_before_after_pixels':stable,
        'unstable_usa_before_after_pixels':unstable,
        'stable_usa_fraction':round(stable/(w*h),8),
        'candidate_probe_only_changed_on_stable_usa_pixels':changed,
        'candidate_probe_only_new_magenta_on_stable_usa_pixels':magenta_candidate,
        'native_magenta_on_stable_usa_pixels':native_magenta,
        'ambiguous_pixels_with_reference_variation':ambiguous,
        'probe_only_changed_bbox_inclusive':box_changed,
        'probe_only_new_magenta_bbox_inclusive':box_magenta,
        'temporal_reference_variation_excluded_from_candidate':True,
        'manual_same_scene_and_frame_alignment_required':True,
        'texture_gpu_identity_proven':False
    }

def audit(manifest_usa_before:Path,manifest_probe:Path,manifest_usa_after:Path,
          iso_usa:Path,iso_probe:Path,report:Path,repo:Path,scene:str,
          roi:tuple[int,int,int,int]|None=None)->dict:
    if not isinstance(scene,str) or not x11.LABEL.fullmatch(scene):
        raise ValueError('Invalid operator scene label')
    box=x11._roi(roi)
    output=x11.private_path(report,repo,for_output=True)
    orig=x11.private_path(iso_usa,repo)
    probe=x11.private_path(iso_probe,repo)
    if orig==probe:raise ValueError('Two independent ISO paths required')
    for path,sha in ((orig,x11.USA_SHA),(probe,x11.PROBE_SHA)):
        if path.stat().st_size!=x11.ISO_SIZE or x11.file_sha(path)!=sha:
            raise ValueError('ISO authenticity hash/size failure')
    manifests=[x11.private_path(Path(p),repo) for p in
               (manifest_usa_before,manifest_probe,manifest_usa_after)]
    if len({p.parent for p in manifests})!=3:
        raise ValueError('A/B/A must use three private session directories')
    a=x11.load_x11(manifests[0],repo,'usa',x11.USA_SHA)
    b=x11.load_x11(manifests[1],repo,'sonda',x11.PROBE_SHA)
    c=x11.load_x11(manifests[2],repo,'usa',x11.USA_SHA)
    pids=[v['window_pid_declared'] for v in (a,b,c)]
    if len(set(pids))!=3:
        raise ValueError('A/B/A requires three independently declared PIDs')
    full=metrics(a['image'],b['image'],c['image'])
    cropped=metrics(*(v['image'].crop(box) for v in (a,b,c))) if box else None
    result={
        'schema':'cladun.f2.x11_aba_temporal_negative_control.v1',
        'scope':'PRIVATE_X11_FILE_COMPARISON_NOT_PSP_FRAMEBUFFER_OR_GAMEPLAY',
        'operator_scene_label_unverified':scene,
        'manifest_sha256':{'usa_before':a['manifest_sha256'],'probe':b['manifest_sha256'],'usa_after':c['manifest_sha256']},
        'png_sha256':{'usa_before':a['png_sha256'],'probe':b['png_sha256'],'usa_after':c['png_sha256']},
        'iso_hashes_verified_on_disk':{'usa':x11.USA_SHA,'probe':x11.PROBE_SHA},
        'declared_distinct_emulator_pids':{'usa_before':pids[0],'probe':pids[1],'usa_after':pids[2]},
        'declared_procfs_witnesses_not_independently_replayed':True,
        'full_frame':full,
        'roi_xyxy_exclusive':list(box) if box else None,
        'roi_frame':cropped,
        'same_scene_alignment_verified':False,
        'same_animation_frame_verified':False,
        'gameplay_skill_or_combat_verified':False,
        'temporal_consistency_establishes_causality':False,
        'loaded_iso_game_identity_proven':False,
        'mips_ram_ge_vram_proven':False,
        'output_contains_commercial_pixel_data':False,
        'warning':'Stable original-before/after only filters temporal differences; a magenta candidate still needs in-game synchronization and authentic GE/MIPS/VRAM texture provenance.'
    }
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('x',encoding='utf-8') as f:
        json.dump(result,f,ensure_ascii=False,indent=2)
        f.write('\n')
    return result

def main()->None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifest-usa-antes',type=Path,required=True)
    p.add_argument('--manifest-sonda',type=Path,required=True)
    p.add_argument('--manifest-usa-despues',type=Path,required=True)
    p.add_argument('--iso-usa',type=Path,required=True)
    p.add_argument('--iso-sonda',type=Path,required=True)
    p.add_argument('--reporte-privado',type=Path,required=True)
    p.add_argument('--escena',required=True)
    p.add_argument('--roi',nargs=4,type=int,metavar=('X','Y','ANCHO','ALTO'))
    args=p.parse_args()
    result=audit(args.manifest_usa_antes,args.manifest_sonda,args.manifest_usa_despues,
                 args.iso_usa,args.iso_sonda,args.reporte_privado,
                 Path(__file__).resolve().parents[1],args.escena,
                 tuple(args.roi) if args.roi else None)
    print(json.dumps({'candidate_new_magenta':result['full_frame']['candidate_probe_only_new_magenta_on_stable_usa_pixels'],
                      'unstable_original_reference_pixels':result['full_frame']['unstable_usa_before_after_pixels'],
                      'same_scene_alignment_verified':False,
                      'mips_ram_ge_vram_proven':False},ensure_ascii=False))

if __name__=='__main__':main()
