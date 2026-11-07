import warp as wp
from tomato_gpu_packet_refresh import PacketEvaluator as ReferenceEvaluator
from tomato_capacity_cad_pressure import CapacityCADPressurePacket
class PacketEvaluator(ReferenceEvaluator):
 def __init__(self,blade,x,rotation,translation,com):
  self.blade=blade;self.x=wp.array(x,dtype=wp.vec3d);self.packet=CapacityCADPressurePacket(len(x));self.rotation=rotation;self.translation=translation;self.com=com
