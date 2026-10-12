import base64,concurrent.futures,datetime,hashlib,json,pathlib,sys,time
sys.path.insert(0,str(pathlib.Path(__file__).parent/'helpers'))
sys.path.insert(0,str(pathlib.Path(__file__).parent/'projects/pa-bpe-simple-20261011'))
from library_hosted_apps import HostedAppsClient
from publish import unpack,save
root=pathlib.Path(__file__).parent;stage=root/'publish_stage';rp=root/'upload_receipts.json';receipts=json.loads(rp.read_text());pending={}
for p in stage.rglob('*'):
    if not p.is_file():continue
    raw=p.read_bytes();sha=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
    if sha not in receipts:pending[sha]=p
client=HostedAppsClient()
def upload(item):
    sha,p=item;raw=p.read_bytes()
    result=unpack(client.call_tool('connector_76869538009648d5b282a4bb21c3d157','create_blob',{'repository_full_name':'Yunbo-max/cpu','encoding':'base64','content':base64.b64encode(raw).decode()}))
    assert result['sha']==sha
    return sha,{'bytes':len(raw),'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'parallel immutable blob only; branch mutation serialized separately'}
print(json.dumps({'pending_unique_blobs':len(pending),'io_workers':4}),flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    for i,future in enumerate(concurrent.futures.as_completed([pool.submit(upload,item) for item in pending.items()]),1):
        sha,receipt=future.result();receipts[sha]=receipt;save(rp,receipts)
        if i%20==0:print(json.dumps({'uploaded':i,'total':len(pending)}),flush=True)
print('all blobs verified',flush=True)
