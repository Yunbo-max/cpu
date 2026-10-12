import hashlib, io, json, sys, urllib.request, zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime, timezone

lang = sys.argv[1]
assert lang in ('en','fr','es')
inventory = json.loads(Path('inputs/tokenized_inventory.json').read_text())
works = [row['work'] for row in inventory['works']]
url = f'https://object.pouta.csc.fi/OPUS-Books/v1/raw/{lang}.zip'
req = urllib.request.Request(url, headers={'User-Agent':'pa-bpe-research/1.0'})
with urllib.request.urlopen(req, timeout=55) as response:
    assert response.status == 200
    blob = response.read(128*1024*1024 + 1)
    headers = dict(response.headers)
assert len(blob) <= 128*1024*1024
out = Path('output/raw') / lang
out.mkdir(parents=True, exist_ok=True)
record = {'observed_utc':datetime.now(timezone.utc).isoformat(), 'url':url,
          'archive_sha256':hashlib.sha256(blob).hexdigest(), 'archive_bytes':len(blob),
          'headers':headers,'members':{}, 'terms':{},'selected_rule':'All 12 works in previously verified three-language XCES intersection; no score-based selection'}
with zipfile.ZipFile(io.BytesIO(blob)) as z:
    names = z.namelist()
    record['archive_member_names'] = names
    for work in works:
        candidates = [n for n in names if Path(n).name == work+'.xml']
        assert len(candidates)==1,(work,candidates)
        name=candidates[0]
        data=z.read(name)
        tree=ET.fromstring(data)
        counts={tag:sum(1 for e in tree.iter() if e.tag.rsplit('}',1)[-1]==tag) for tag in ['s','w','chunk']}
        assert counts['s']>0 and counts['w']==0 and counts['chunk']==0,(work,counts)
        path=out/(work+'.xml');path.write_bytes(data)
        record['members'][work]={'archive_member':name,'path':str(path),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'xml_elements':counts}
    for n in names:
        if n in ['LICENSE','README','INFO']:
            data=z.read(n);(out/n).write_bytes(data)
            record['terms'][n]={'sha256':hashlib.sha256(data).hexdigest(),'text':data.decode(errors='replace')}
Path(f'output/raw_{lang}_manifest.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'language':lang,'archive_bytes':len(blob),'works':len(record['members']),'source':url}))
