"""Fixed native analytic slab minimizer queries; no contacts, forces or steps."""
import argparse
import math
from pathlib import Path
import signal
import traceback
from tomato_isaac_startup_worker import write


def fixture_cases():
    cases=[]
    for shift in (0.,-1e-7,1e-7,-1e-5,1e-5):
        cases.append({'id':f'cross:{shift}', 'a':[0.,0.,-.01+shift], 'b':[0.,0.,.01+shift],
                      'minimum_normal_ambiguous':True})
    for name,z in [('top',.001),('bottom',-.001),('clear',.003)]:
        cases.append({'id':name,'a':[-.01,0.,z],'b':[.01,0.,z],
                      'minimum_normal_ambiguous':False})
    return [dict(c,id=c['id']+suffix,a=c['b'] if reverse else c['a'],
                 b=c['a'] if reverse else c['b'],reversed=reverse)
            for c in cases for reverse,suffix in ((False,':forward'),(True,':reverse'))]


def expected_minimum(a,b,h):
    low,high=sorted((a[2],b[2]))
    return (0. if low <= 0 <= high else min(abs(low),abs(high)))-h


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    out=parser.parse_args().output
    def stop(signum,frame):raise InterruptedError('Native slab query stopped')
    signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
    try:
        import warp as wp
        from newton._src.geometry.soft_contacts_sdf import optimize_edge_sdf, eval_shape_sdf, SDF_EDGE_ITERS
        from newton._src.geometry.sdf_texture import TextureSDFData
        from newton._src.geometry.types import GeoType
        wp.init();wp.set_device('cuda:0')
        cases=fixture_cases()
        a=wp.array([c['a'] for c in cases],dtype=wp.vec3);b=wp.array([c['b'] for c in cases],dtype=wp.vec3)
        table=wp.empty(0,dtype=TextureSDFData)
        parameters=wp.array([[.1,.1,.002]],dtype=wp.vec3)
        u=wp.zeros(16,dtype=float);x=wp.zeros(16,dtype=wp.vec3);phi=wp.zeros(16,dtype=float);normal=wp.zeros(16,dtype=wp.vec3)

        @wp.kernel(enable_backward=False)
        def query(a:wp.array[wp.vec3],b:wp.array[wp.vec3],scale:wp.array[wp.vec3],
                  table:wp.array[TextureSDFData],geo:int,iters:int,
                  u:wp.array[float],x:wp.array[wp.vec3],phi:wp.array[float],normal:wp.array[wp.vec3]):
            i=wp.tid()
            value,point,distance,gradient=optimize_edge_sdf(geo,scale[0],a[i],b[i],-1,table,iters)
            u[i]=value;x[i]=point;phi[i]=distance;normal[i]=gradient

        @wp.kernel(enable_backward=False)
        def direct(points:wp.array[wp.vec3],scale:wp.array[wp.vec3],table:wp.array[TextureSDFData],geo:int,
                   phi:wp.array[float],normal:wp.array[wp.vec3]):
            i=wp.tid()
            lower,value,gradient=eval_shape_sdf(geo,scale[0],points[i],-1,table)
            phi[i]=value;normal[i]=gradient

        if (out/'stop.request').exists():raise InterruptedError('Stopped before slab queries')
        write(out,'worker_status.json',{'stage':'native_slab_minimizer_queries'})
        wp.launch(query,dim=16,inputs=[a,b,parameters,table,int(GeoType.BOX),SDF_EDGE_ITERS],outputs=[u,x,phi,normal])
        direct_points=wp.array([[0.,0.,-1e-9],[0.,0.,0.],[0.,0.,1e-9]],dtype=wp.vec3)
        direct_phi=wp.zeros(3,dtype=float);direct_normal=wp.zeros(3,dtype=wp.vec3)
        wp.launch(direct,dim=3,inputs=[direct_points,parameters,table,int(GeoType.BOX)],outputs=[direct_phi,direct_normal])
        wp.synchronize()
        ah,bh=a.numpy().tolist(),b.numpy().tolist();uh,xh,dh,nh=u.numpy().tolist(),x.numpy().tolist(),phi.numpy().tolist(),normal.numpy().tolist()
        h=parameters.numpy().tolist()[0][2];results=[]
        for i,c in enumerate(cases):
            if not all(math.isfinite(v) for v in [uh[i],dh[i],*xh[i],*nh[i]]) or not 0<=uh[i]<=1:
                raise ValueError('Invalid native query result')
            expected=expected_minimum(ah[i],bh[i],h)
            interpolation=math.dist(xh[i],[(1-uh[i])*p+uh[i]*q for p,q in zip(ah[i],bh[i])])
            phi_at_point=abs(xh[i][2])-h
            if abs(dh[i]-expected)>1e-6 or abs(dh[i]-phi_at_point)>1e-8 or interpolation>1e-7:
                raise ValueError('Native minimum/point arithmetic differs from analytic slab reference')
            if not c['minimum_normal_ambiguous']:
                expected_normal=[0.,0.,1. if ah[i][2]>0 else -1.]
                if math.dist(nh[i],expected_normal)>1e-6:raise ValueError('Unique-branch control normal mismatch')
            results.append(dict(c,native_a_m=ah[i],native_b_m=bh[i],native_u=uh[i],native_point_m=xh[i],
                native_phi_m=dh[i],native_normal=nh[i],analytic_minimum_phi_m=expected,
                minimum_distance_error_m=abs(dh[i]-expected),interpolation_error_m=interpolation))
        comparisons=[]
        for i in range(0,16,2):
            forward,reverse=results[i:i+2]
            comparisons.append({'pair':forward['id'].removesuffix(':forward'),
                'normal_dot':sum(p*q for p,q in zip(forward['native_normal'],reverse['native_normal'])),
                'point_separation_m':math.dist(forward['native_point_m'],reverse['native_point_m']),
                'phi_difference_m':abs(forward['native_phi_m']-reverse['native_phi_m'])})
        direct_rows=[{'point_m':p,'native_phi_m':d,'native_normal':n} for p,d,n in
                     zip(direct_points.numpy().tolist(),direct_phi.numpy().tolist(),direct_normal.numpy().tolist())]
        if not all(math.isfinite(v) for row in direct_rows for v in [row['native_phi_m'],*row['native_normal']]):
            raise ValueError('Invalid direct SDF result')
        for row in direct_rows:
            z=row['point_m'][2]
            if abs(row['native_phi_m']-(abs(z)-h))>1e-8:
                raise ValueError('Direct slab distance mismatch')
            if z != 0 and math.dist(row['native_normal'],[0.,0.,1. if z>0 else -1.])>1e-6:
                raise ValueError('Direct unique branch normal mismatch')
        write(out,'native_slab_measurements.json',{'cases':results,'reversal_comparisons':comparisons,
            'direct_queries':direct_rows,'edge_iterations':SDF_EDGE_ITERS,'optimizer_queries':16,'direct_query_count':3,
            'query_count':19,'mechanical_steps':0,'force_evaluations':0,
            'numerical_comparison_scope':'Analytic slab only: minimum phi 1e-6 m, returned-point phi 1e-8 m, interpolation 1e-7 m; no physical thresholds changed.',
            'normal_branch_stability_validated':False,'full_surface_contact_validated':False})
        write(out,'worker_result.json',{'diagnostic_passed':True,'shutdown_requested':True,
            'slab_optimizer_cases_completed':16,'slab_queries_completed':19,'mechanical_steps':0,'force_evaluations':0,
            'training':False,'full_surface_contact_validated':False})
        return 0
    except BaseException:
        write(out,'worker_failure.json',{'traceback':traceback.format_exc()})
        write(out,'worker_result.json',{'diagnostic_passed':False,'shutdown_requested':True})
        traceback.print_exc();return 1


if __name__=='__main__':raise SystemExit(main())
