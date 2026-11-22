#!/usr/bin/env python3
"""F2: dos capturas PNG reales mediante PPSSPP 1.20.4 WebSocket LOCAL.

Todo archivo generado va a una carpeta privada FUERA del repositorio.
NO es una traza GE/MIPS/VRAM completa; no falsificar esa conclusión.
La dependencia websocket-client es opcional y solo se importa al conectar.
La GPU en v1.20.4 requiere CPU/GPU detenida para framebuffer;
la grabación de siguiente frame necesita CPU en ejecución.
"""
from __future__ import annotations
import argparse,base64,hashlib,json,re,time
from pathlib import Path

def digest(data):return hashlib.sha256(data).hexdigest()

def parse_uri(uri,mime='image/png',max_bytes=50*1024*1024):
    prefix='data:'+mime+';base64,'
    if not isinstance(uri,str) or not uri.startswith(prefix):
        raise ValueError('Respuesta de imagen/URI inválida')
    if len(uri)-len(prefix)>((max_bytes+2)//3)*4+4:
        raise ValueError('Respuesta demasiado grande')
    try:data=base64.b64decode(uri[len(prefix):],validate=True)
    except Exception as exc:raise ValueError('Base64 inválido') from exc
    if len(data)>max_bytes:raise ValueError('Payload demasiado grande')
    return data

def output_dir(dest,repo):
    dest,repo=Path(dest).resolve(),Path(repo).resolve()
    if dest==repo or repo in dest.parents or any((p/'.git').exists() for p in (dest,*dest.parents)):
        raise ValueError('Prohibido guardar imágenes comerciales en un repositorio')
    if dest.exists() and any(dest.iterdir()):
        raise FileExistsError('Usar directorio de evidencias NUEVO')
    dest.mkdir(parents=True,exist_ok=True)
    return dest

def exclusive(path,data):
    if not data:raise ValueError('No aceptar evidencia vacía')
    with path.open('xb') as f:f.write(data)
    return {'name':path.name,'bytes':len(data),'sha256':digest(data)}

class Client:
    def __init__(self,conn):
        self.conn=conn
        self.ticket=0
        self._broadcasts=[]  # Unsolicited debugger events may arrive before replies
    def request(self,event,**kwargs):
        self.ticket+=1;ticket=self.ticket
        self.conn.send(json.dumps({'event':event,'ticket':ticket,**kwargs}))
        for _ in range(1000):
            msg=json.loads(self.conn.recv())
            if msg.get('ticket')!=ticket:
                if msg.get('ticket') is None:
                    if msg.get('event')=='error':
                        raise RuntimeError('Error asíncrono del depurador: '+str(msg.get('message')))
                    if len(self._broadcasts)>=256:
                        raise RuntimeError('Cola de eventos PPSSPP excedida; no descartar silenciosamente')
                    self._broadcasts.append(msg)
                continue
            if msg.get('event')=='error':raise RuntimeError(f'{event}: '+str(msg.get('message')))
            if msg.get('event')!=event:raise ValueError('Ticket correlacionado a evento incorrecto')
            return msg
        raise TimeoutError('Respuestas WebSocket sin ticket esperado')

    def notify(self,event,**kwargs):
        """PPSSPP cpu.stepping/resume do NOT reply with the request ticket."""
        # Do not mistake an event already processed by a prior command for a
        # new pause/resume. Broadcasts still waiting on the socket are verified
        # independently using cpu.status and observed emulation ticks.
        self._broadcasts=[x for x in self._broadcasts if x.get('event')!=event]
        self.conn.send(json.dumps({'event':event,**kwargs}))

    def wait_broadcast(self,event):
        for i,msg in enumerate(self._broadcasts):
            if msg.get('event')==event:
                self._broadcasts.pop(i)
                return msg
        for _ in range(1000):
            msg=json.loads(self.conn.recv())
            if msg.get('event')=='error' and 'ticket' not in msg:
                raise RuntimeError(f'{event}: '+str(msg.get('message')))
            if msg.get('event')==event and 'ticket' not in msg:
                return msg
            if msg.get('ticket') is None:
                if len(self._broadcasts)>=256:
                    raise RuntimeError('Cola de eventos PPSSPP excedida')
                self._broadcasts.append(msg)
            else:
                raise RuntimeError('Respuesta con ticket inesperado esperando evento '+event)
        raise TimeoutError('No llegó el evento broadcast '+event)


def _pause_for_gpu_read(client):
    """PPSSPP v1.20.4 GPUBufferSubscriber rejects requests while CPU is running."""
    status=client.request('cpu.status')
    if status.get('stepping') is True:
        return False,status.get('ticks')
    client.notify('cpu.stepping')
    step=client.wait_broadcast('cpu.stepping')
    if client.request('cpu.status').get('stepping') is not True:
        raise RuntimeError('La CPU no confirmó la pausa antes de leer la GPU')
    return True,step.get('ticks')


def _resume_after_gpu_read(client,paused_here):
    if paused_here:
        client.notify('cpu.resume')
        client.wait_broadcast('cpu.resume')

def capture(client,scene,folder,ge_dump=False):
    """Real GPU readbacks need a stepping CPU; GE next-frame recorder needs a RUNNING CPU.

    These images represent the PSP output framebuffer, NOT the 960x544 desktop
    window. Never pass them off as the old F1 window-size regression screenshots.
    """
    shots=[]
    gpu=None
    if ge_dump:
        if client.request('cpu.status').get('stepping') is True:
            raise RuntimeError('Para gpu.record.dump la CPU debe estar ejecutándose; reanúdala primero')
        # PPSSPP GPURecordSubscriber records NEXT frame asynchronously.
        resp=client.request('gpu.record.dump')
        raw=parse_uri(resp.get('uri'),'application/octet-stream',256*1024*1024)
        if raw[:8]!=b'PPSSPPGE':
            raise ValueError('La grabación no contiene cabecera PPSSPPGE')
        gpu=exclusive(folder/f'{scene}_GE_PRIVATE.dump',raw)
    for i in range(2):
        paused_here,ticks=_pause_for_gpu_read(client)
        try:
            response=client.request('gpu.buffer.screenshot',type='uri')
            png=parse_uri(response.get('uri'))
            if not png.startswith(b'\x89PNG\r\n\x1a\n'):
                raise ValueError('No se recibió PNG auténtico')
            shot=exclusive(folder/f'{scene}_{i+1:02d}.png',png)
            shot['psp_framebuffer_width']=response.get('width')
            shot['psp_framebuffer_height']=response.get('height')
            shot['emulated_ticks_at_pause']=ticks
            shots.append(shot)
        finally:
            # Preserve externally established debugger pauses, including failures.
            _resume_after_gpu_read(client,paused_here)
        if i==0:time.sleep(0.4)
    return {'screenshots':shots,'gpu_record':gpu,
            'source':'gpu.buffer.screenshot on paused PSP emulator (not desktop window)',
            'two_distinct_frames_proven':len(shots)==2 and
                all(isinstance(s.get('emulated_ticks_at_pause'),(int,float)) for s in shots) and
                shots[1]['emulated_ticks_at_pause']>shots[0]['emulated_ticks_at_pause'],
            'f1_960x544_window_regression_proven':False}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scene',required=True)
    parser.add_argument('--salida-privada',type=Path,required=True)
    parser.add_argument('--port',type=int,default=24192)
    parser.add_argument('--ge-dump',action='store_true')
    args=parser.parse_args()
    if not re.fullmatch('[A-Za-z0-9_-]{1,48}',args.scene):parser.error('Escena inválida')
    if not 1<=args.port<=65535:parser.error('Puerto incorrecto')
    folder=output_dir(args.salida_privada,Path(__file__).resolve().parents[1])
    try:import websocket
    except ImportError as exc:raise RuntimeError('Instalar websocket-client para conectar a PPSSPP') from exc
    conn=websocket.create_connection('ws://127.0.0.1:%d/debugger'%args.port,
                                     subprotocols=['debugger.ppsspp.org'],timeout=60)
    try:
        if conn.getsubprotocol()!='debugger.ppsspp.org':
            raise RuntimeError('El servidor no habla el protocolo PPSSPP')
        client=Client(conn)
        ver=client.request('version',name='cladun-f2',version='1')
        if ver.get('name')!='PPSSPP' or not str(ver.get('version','')).startswith('v1.20.4'):
            raise RuntimeError('Esta sonda requiere PPSSPP 1.20.4')
        game=client.request('game.status').get('game')
        if not isinstance(game,dict) or 'cladun' not in str(game.get('title','')).lower():
            raise RuntimeError('Cladun no está iniciado')
        # PC conocido corresponde a búsqueda de TEXTO, NO dibujo de iconos.
        mips=client.request('memory.disasm',address=0x089089A0,count=32).get('lines',[])
        report={'schema':'cladun.f2.ppsspp_private_v1204.v1',
                'runtime':'PPSSPP REAL SOLO CUANDO SE CONECTA A UN EMULADOR',
                'ppsspp':ver.get('version'),'game':game,'scene':args.scene,
                'mips_lookup_text':mips,
                'captures':capture(client,args.scene,folder,args.ge_dump),
                'ge_vram_pipeline_proven':False,
                'nineteen_glyphs_multiscene_proven':False}
        encoded=(json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode()
        manifest=exclusive(folder/'manifest_PRIVATE.json',encoded)
        print(json.dumps({'manifest':manifest,'png':report['captures']['screenshots'],
                          'ge_vram_pipeline_proven':False},ensure_ascii=False,indent=2))
    finally:conn.close()
if __name__=='__main__':main()
