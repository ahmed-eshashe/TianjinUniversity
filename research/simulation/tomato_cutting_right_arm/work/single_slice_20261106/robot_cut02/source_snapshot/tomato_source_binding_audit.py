"""AST-only native binder compatibility audit; never imports installed engines."""
import ast
from pathlib import Path


def function(source,cls,name):
    tree=ast.parse(source)
    for part in cls.split('.') if cls else []:
        tree=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name==part)
    return next(n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name)


def check_call(callee,call,*,expanded_keywords=()):
    positional=list(callee.args.posonlyargs)+list(callee.args.args)
    if positional and positional[0].arg in ('self','cls'):positional=positional[1:]
    allowed={a.arg for a in positional+list(callee.args.kwonlyargs)}
    names=[k.arg for k in call.keywords if k.arg is not None]+list(expanded_keywords)
    unknown=set(names)-allowed
    if unknown and callee.args.kwarg is None:raise ValueError('Unknown native keyword: '+','.join(sorted(unknown)))
    if len(names)!=len(set(names)):raise ValueError('Duplicate expanded keyword')
    if any(isinstance(a,ast.Starred) for a in call.args):raise ValueError('Unresolved native positional expansion')
    if len(call.args)>len(positional) and callee.args.vararg is None:raise ValueError('Native positional arity mismatch')
    if any(k.arg is None for k in call.keywords) and not expanded_keywords:raise ValueError('Unresolved native keyword expansion')
    supplied={a.arg for a in positional[:len(call.args)]}|set(names)
    if set(a.arg for a in positional[:len(positional)-len(callee.args.defaults)])-supplied:
        raise ValueError('Missing required native positional argument')
    required_kw={a.arg for a,default in zip(callee.args.kwonlyargs,callee.args.kw_defaults) if default is None}
    if required_kw-supplied:raise ValueError('Missing required native keyword-only argument')
    if {a.arg for a in positional[:len(call.args)]}&set(names):raise ValueError('Native positional/keyword duplicate')
    return {'explicit_keywords_checked':names,'positional_count':len(call.args),'runtime_types_validated':False}


def audit(root,installed):
    root=Path(root);installed=Path(installed)
    files={'builder':installed/'sim/builder.py','solver':installed/'solvers/vbd/solver_vbd.py',
           'pipeline':installed/'sim/collide.py','types':installed/'geometry/types.py',
           'helper':installed/'solvers/vbd/rigid_vbd_kernels.py'}
    text={k:p.read_text() for k,p in files.items()}
    routes={'newton.ModelBuilder':('builder','ModelBuilder','__init__'),
      'newton.Mesh':('types','Mesh','__init__'),'newton.solvers.SolverVBD':('solver','SolverVBD','__init__'),
      'newton.CollisionPipeline':('pipeline','CollisionPipeline','__init__'),
      'shape.configure_sdf':('builder','ModelBuilder.ShapeConfig','configure_sdf')}
    for method in ('add_particle','add_spring','add_triangle','add_body','add_shape_mesh','color','finalize'):
        routes['builder.'+method]=('builder','ModelBuilder',method)
    checks=[]
    for filename in ('tomato_native_coupon.py','tomato_two_piece_coupon.py'):
        tree=ast.parse((root/'rl'/filename).read_text());expanded=()
        if filename=='tomato_two_piece_coupon.py':
            dictionaries=[v for n in ast.walk(tree) if isinstance(n,ast.Dict) for k,v in zip(n.keys,n.values) if isinstance(k,ast.Constant) and k.value=='self_contact_solver_options']
            expanded=tuple(k.value for k in dictionaries[0].keys)
        for call in [n for n in ast.walk(tree) if isinstance(n,ast.Call)]:
            name=ast.unparse(call.func)
            if name in routes:
                file,cls,method=routes[name];r=check_call(function(text[file],cls,method),call,expanded_keywords=expanded if any(k.arg is None for k in call.keywords) else ())
                checks.append({'source':filename,'line':call.lineno,'target':name,**r})
    observer=ast.parse((root/'rl/tomato_soft_contact_observer.py').read_text())
    call=next(n for n in ast.walk(observer) if isinstance(n,ast.Call) and ast.unparse(n.func)=='_eval_soft_ef_contact')
    helper=function(text['helper'],'','_eval_soft_ef_contact')
    if len(helper.args.args)!=len(call.args):raise ValueError('Private observer helper positional count drift')
    arguments=[{'parameter':a.arg,'expression':ast.unparse(v)} for a,v in zip(helper.args.args,call.args)]
    extended=step_registry_audit(root,installed)
    config_class=next(n for n in ast.walk(ast.parse(text['builder'])) if isinstance(n,ast.ClassDef) and n.name=='ShapeConfig')
    config_fields={n.target.id for n in config_class.body if isinstance(n,ast.AnnAssign) and isinstance(n.target,ast.Name)}
    for filename in ('tomato_native_coupon.py','tomato_two_piece_coupon.py'):
        for n in ast.walk(ast.parse((root/'rl'/filename).read_text())):
            if isinstance(n,ast.Call) and ast.unparse(n.func)=='newton.ModelBuilder.ShapeConfig':
                if any(k.arg not in config_fields for k in n.keywords):raise ValueError('Unknown generated ShapeConfig field')
    return {**extended,'generated_ShapeConfig_fields_checked':True,'constructor_and_method_calls':checks,'private_helper_argument_map':arguments,
      'native_runtime_validated':False,'kernel_compiled':False,'array_dtype_and_device_validated':False,
      'semantic_argument_review_required':True,'inspected_source_paths':{k:str(p) for k,p in files.items()}}


def declared_attributes(source,cls):
    tree=next(n for n in ast.parse(source).body if isinstance(n,ast.ClassDef) and n.name==cls)
    names={n.name for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
    for n in ast.walk(tree):
        if isinstance(n,(ast.Assign,ast.AnnAssign)):
            targets=n.targets if isinstance(n,ast.Assign) else [n.target]
            for t in targets:
                if isinstance(t,ast.Attribute) and isinstance(t.value,ast.Name) and t.value.id=='self':names.add(t.attr)
                elif isinstance(t,ast.Name) and isinstance(n,ast.AnnAssign):names.add(t.id)
    return names


def step_registry_audit(root,installed):
    sources={'model':(installed/'sim/model.py','Model'),
        'solver':(installed/'solvers/vbd/solver_vbd.py','SolverVBD'),
        'contacts':(installed/'sim/contacts.py','Contacts'),
        'pipeline':(installed/'sim/collide.py','CollisionPipeline'),
        's0':(installed/'sim/state.py','State'),'s1':(installed/'sim/state.py','State')}
    declarations={name:declared_attributes(path.read_text(),cls) for name,(path,cls) in sources.items()}
    tree=ast.parse((root/'rl/tomato_native_step.py').read_text());fields={}
    for node in ast.walk(tree):
        if isinstance(node,ast.Attribute) and isinstance(node.value,ast.Name) and node.value.id in declarations:
            owner=node.value.id
            if node.attr not in declarations[owner]:raise ValueError('Undeclared installed source field: '+owner+'.'+node.attr)
            fields.setdefault(owner,set()).add(node.attr)
    launch=next(n for n in ast.walk(tree) if isinstance(n,ast.Call) and ast.unparse(n.func)=='wp.launch' and n.args and ast.unparse(n.args[0])=='observer_kernel')
    arrays={k.arg:k.value for k in launch.keywords}
    if not isinstance(arrays.get('inputs'),ast.List) or not isinstance(arrays.get('outputs'),ast.List):raise ValueError('Unresolved observer launch lists')
    observer=next(n for n in ast.walk(ast.parse((root/'rl/tomato_soft_contact_observer.py').read_text())) if isinstance(n,ast.FunctionDef) and n.name=='observe')
    count=len(arrays['inputs'].elts)+len(arrays['outputs'].elts)
    if count!=len(observer.args.args):raise ValueError('Observer kernel launch arity mismatch')
    return {'step_field_declarations_checked':{k:sorted(v) for k,v in fields.items()},
        'observer_kernel_launch_argument_count':count,'declaration_presence_is_runtime_layout_validation':False}
