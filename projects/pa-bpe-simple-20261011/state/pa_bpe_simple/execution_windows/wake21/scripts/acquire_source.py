import datetime, hashlib, json, resource, sys, urllib.request
from pathlib import Path

resource.setrlimit(resource.RLIMIT_AS, (256*1024**2, 256*1024**2))
index = int(sys.argv[1])
spec = json.loads(Path('tatoeba_confirmation_protocol.json').read_text())['source']['files'][index]
dest = Path('output') / spec['url'].rsplit('/', 1)[1]
record = {'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'spec': spec,
          'role': spec['role'], 'status': 'started', 'text_parsed': False}
out = Path('output') / (spec['role'] + '.source.json')
try:
    assert not dest.exists(), 'Do not overwrite existing source bytes'
    digest = hashlib.sha256(); count = 0
    with urllib.request.urlopen(spec['url'], timeout=35) as response, dest.open('xb') as f:
        record['headers'] = dict(response.headers.items())
        record['response_url'] = response.url
        while True:
            block = response.read(65536)
            if not block: break
            f.write(block); digest.update(block); count += len(block)
            if count > spec['directory_size_bytes']: raise ValueError('frozen_size_exceeded')
    record.update(bytes=count, sha256=digest.hexdigest())
    assert count == spec['directory_size_bytes'], 'frozen_size_mismatch'
    record['status'] = 'size_and_hash_recorded_not_yet_semantically_validated'
except BaseException as exc:
    record.update(status='failed', error=repr(exc))
    if dest.exists():
        record['partial_bytes'] = dest.stat().st_size
        h=hashlib.sha256()
        with dest.open('rb') as f:
            for b in iter(lambda:f.read(65536),b''):h.update(b)
        record['partial_sha256']=h.hexdigest()
    raise
finally:
    out.write_text(json.dumps(record, indent=2)+'\n')
print(json.dumps(record))
