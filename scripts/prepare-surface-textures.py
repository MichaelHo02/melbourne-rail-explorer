"""Download the selected 1K CC0 Poly Haven PBR surfaces, retaining provenance."""
import json, pathlib, urllib.request

ROOT=pathlib.Path(__file__).resolve().parents[1]
TARGET=ROOT/'public/textures/surfaces'
ASSETS={'ballast':'gravel_stones','asphalt':'asphalt_02','paving':'pavement_04'}

def fetch(url):
    request=urllib.request.Request(url,headers={'User-Agent':'MelbourneRailExplorer/0.1 (CC0 game asset preparation)'})
    with urllib.request.urlopen(request,timeout=60) as response:return response.read()

TARGET.mkdir(parents=True,exist_ok=True)
manifest=[]
for name,asset in ASSETS.items():
    files=json.loads(fetch('https://api.polyhaven.com/files/'+asset))
    info=json.loads(fetch('https://api.polyhaven.com/info/'+asset))
    entry={'name':name,'asset':asset,'url':'https://polyhaven.com/a/'+asset,'license':'CC0',
           'licenseUrl':'https://polyhaven.com/license','authors':info.get('authors'),
           'dimensionsMillimetres':info.get('dimensions'),'maps':{}}
    for channel,source_channel in [('diff','Diffuse'),('nor_gl','nor_gl'),('rough','Rough')]:
        source=files[source_channel]['1k']['jpg']['url']
        path=TARGET/(name+'-'+channel+'.jpg')
        payload=fetch(source);path.write_bytes(payload)
        entry['maps'][channel]={'file':path.name,'source':source,'bytes':len(payload)}
    manifest.append(entry)
    print(asset,sum(item['bytes'] for item in entry['maps'].values()),'bytes')
(TARGET/'sources.json').write_text(json.dumps(manifest,indent=2)+'\n')
