"""Conservative local import closure, archived before a native experiment."""
import ast,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def capture_sources(output,modules,inputs=()):
 output=Path(output);output.mkdir(parents=True,exist_ok=True);pending=[Path(p) for p in modules]+[Path(__file__)];files=set(map(Path,inputs));seen=set()
 while pending:
  p=pending.pop().resolve()
  if p in seen:continue
  seen.add(p);files.add(p)
  if p.suffix!='.py':continue
  for node in ast.walk(ast.parse(p.read_text())):
   names=[node.module] if isinstance(node,ast.ImportFrom) and node.module else [a.name for a in node.names] if isinstance(node,ast.Import) else []
   for name in names:
    if name.startswith('tomato_'):
     child=ROOT/'rl'/(name.split('.')[0]+'.py')
     if child.exists():pending.append(child)
 pins={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)};copies={}
 for name,h in pins.items():
  p=Path(name);relative=p.relative_to(ROOT) if p.is_relative_to(ROOT) else Path('external')/p.name;dest=output/'source_snapshot'/relative;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes());copies[name]=str(dest.relative_to(output))
 (output/'source_closure.json').write_text(json.dumps(dict(scope='Conservative static local import closure; includes nonexecuted local branches',source_sha256=pins,archived_paths=copies),indent=2)+'\n');return pins

def sources_unchanged(pins):return all(Path(p).exists() and hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in pins.items())
