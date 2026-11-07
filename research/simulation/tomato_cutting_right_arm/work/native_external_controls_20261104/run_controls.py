from pathlib import Path
import subprocess,json,os,hashlib
w=Path(__file__).resolve().parent;r=w.parents[1];p=r/'work/native_instrumentation_20261102/PhysX';b=p/'omni/ovexts/_compiler/gcc-linux-x86_64/build-release/physx_sdk/sdk_source_bin'
cmd=['g++','-std=c++17','-O2','-DNDEBUG','-DPX_PHYSX_STATIC_LIB','-I'+str(p/'physx/include'),str(w/'coupled_control.cpp'),'-Wl,--start-group']+[str(b/('lib'+n+'_static.a')) for n in ['PhysX','PhysXCommon','PhysXFoundation','PhysXExtensions','PhysXPvdSDK','PhysXCooking']]+['-Wl,--end-group','-lpthread','-ldl','-o',str(w/'coupled_control')]
x=subprocess.run(cmd,capture_output=True,text=True,timeout=120);(w/'compile.log').write_text(x.stdout+x.stderr);assert x.returncode==0,x.stderr
contract={'scope':'Two collinear prismatic joints, fixed base, masses2and3kg, no gravity/contact/drives/damping','mass_matrix':[[5,3],[3,3]],'actuation_cases':[[0,0],[1,2]],'dt':1/240,'steps_each':2,'iterations':[32,8],'momentum_absolute_tolerance':1e-7,'energy_absolute_tolerance_j':1e-8,'source_sha256':hashlib.sha256((w/'coupled_control.cpp').read_bytes()).hexdigest(),'qualified_robot_work':False};(w/'contract.json').write_text(json.dumps(contract,indent=2)+'\n')
for name,target,trace in [('zero',0,True),('driven_off',1,False),('driven_on',1,True)]:
 d=w/name;d.mkdir();env=dict(os.environ);env.pop('TOMATO_NATIVE_EXTERNAL_TRACE',None)
 if trace:env['TOMATO_NATIVE_EXTERNAL_TRACE']=str(d/'external.csv')
 x=subprocess.run([str(w/'coupled_control'),str(target)],env=env,capture_output=True,text=True,timeout=20);(d/'states.csv').write_text(x.stdout);(d/'stderr.log').write_text(x.stderr);(d/'result.json').write_text(json.dumps({'exit_code':x.returncode})+'\n');print(name,x.returncode,x.stdout,x.stderr)
