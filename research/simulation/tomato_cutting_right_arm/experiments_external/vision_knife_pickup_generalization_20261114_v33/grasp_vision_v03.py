"""Factorized head RGB-D perception: visible landmarks, grasp offset and height."""
import torch
from torch import nn
from torch.nn import functional as F
from grasp_vision_v02 import prepare_image,coordinates

class GraspVision(nn.Module):
    def __init__(self):
        super().__init__()
        self.features=nn.Sequential(nn.Conv2d(5,16,5,2,2),nn.SiLU(),nn.Conv2d(16,32,5,2,2),nn.SiLU(),nn.Conv2d(32,48,5,1,2),nn.SiLU(),nn.Conv2d(48,32,5,1,2),nn.SiLU())
        self.landmarks=nn.Conv2d(32,2,1)
        self.context=nn.Sequential(nn.Conv2d(32,48,5,2,2),nn.SiLU(),nn.Conv2d(48,64,5,2,2),nn.SiLU(),nn.Conv2d(64,64,5,2,2),nn.SiLU(),nn.Conv2d(64,32,5,1,2),nn.SiLU())
        self.geometry=nn.Sequential(nn.Linear(104,64),nn.SiLU(),nn.Linear(64,3),nn.Tanh())
    def forward(self,im):
        features=self.features(im);logits=self.landmarks(features);xy,_=coordinates(logits)
        prob=logits.float().flatten(2).softmax(-1)
        context=F.interpolate(self.context(features),size=features.shape[-2:],mode='bilinear',align_corners=False)
        local=torch.einsum('bkn,bcn->bkc',prob,context.float().flatten(2)).flatten(1)
        norm=(xy-xy.new_tensor([96.,96.]))/xy.new_tensor([447.,319.])*2-1
        sensor=F.grid_sample(im[:,3:5].float(),norm[:,:,None],align_corners=True).flatten(1)
        geometry=self.geometry(torch.cat([local,context.float().mean((2,3)),norm.flatten(1),sensor],1))
        return logits,geometry[:,:2]*.015,geometry[:,2]*.03
