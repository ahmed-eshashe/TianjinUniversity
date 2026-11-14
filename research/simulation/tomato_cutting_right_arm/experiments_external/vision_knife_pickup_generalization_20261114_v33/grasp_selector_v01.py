"""Learn known-geometry/rest-face grasp choice from head RGB-D only."""
import torch
from torch import nn
from torch.nn import functional as F
from grasp_vision_v02 import prepare_image
class GraspSelector(nn.Module):
 def __init__(self):
  super().__init__()
  self.net=nn.Sequential(nn.Conv2d(5,16,5,2,2),nn.SiLU(),nn.Conv2d(16,32,5,2,2),nn.SiLU(),nn.Conv2d(32,64,5,2,2),nn.SiLU(),nn.Conv2d(64,64,5,2,2),nn.SiLU(),nn.AdaptiveAvgPool2d((4,4)),nn.Flatten(),nn.Linear(1024,128),nn.SiLU(),nn.Linear(128,6))
 def forward(self,x):return self.net(F.interpolate(x,size=(160,224),mode='bilinear',align_corners=False))
