"""Check immutable input/source hashes in a prepared distribution."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
manifest=json.loads((ROOT/'MANIFEST.json').read_text(encoding='utf-8'))
for name,digest in manifest['files_sha256'].items():
    p=(ROOT/name).resolve();assert p.is_relative_to(ROOT.resolve())
    assert p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==digest,name
print(json.dumps({'status':'PASS_PACKAGE_HASHES','files':len(manifest['files_sha256'])}))
