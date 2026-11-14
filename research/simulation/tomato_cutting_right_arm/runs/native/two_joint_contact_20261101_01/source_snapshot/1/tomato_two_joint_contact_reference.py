"""Initial-rest planar 2R response to an independently predicted contact wrench."""
from tomato_two_joint_reference import reference,check

def expected_response(angle,wrench,dt):
    result=reference(angle,dt)
    effort=[sum(result['jacobian'][k][j]*wrench[k] for k in range(6)) for j in range(2)]
    a,b=result['matrix'][0];_,d=result['matrix'][1];det=a*d-b*b
    acc=[(d*effort[0]-b*effort[1])/det,(a*effort[1]-b*effort[0])/det]
    result.update(wrench=list(wrench),effort=effort,velocity=[dt*x for x in acc],position=[17/32*dt*dt*x for x in acc])
    return result
