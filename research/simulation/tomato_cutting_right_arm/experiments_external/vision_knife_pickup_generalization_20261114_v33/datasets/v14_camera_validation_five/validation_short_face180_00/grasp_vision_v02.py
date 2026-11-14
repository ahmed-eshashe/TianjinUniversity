"""Learn grasp landmarks and resting-height correction from head RGB-D only."""
import torch
from torch import nn
from torch.nn import functional as F
from vision_policy import image_tensor

CROP=(96,96,544,416)

def prepare_image(rgb,depth,device):
    im=image_tensor(rgb,depth,device)
    assert im.shape[-2:]==(480,640)
    return im[...,96:416,96:544]

def coordinates(logits):
    p=logits.float().flatten(2).softmax(-1)
    yy,xx=torch.meshgrid(torch.arange(logits.shape[2],device=logits.device)*4.+96.,
                         torch.arange(logits.shape[3],device=logits.device)*4.+96.,indexing='ij')
    xy=torch.stack([(p*xx.flatten()).sum(-1),(p*yy.flatten()).sum(-1)],-1)
    return xy,p.amax(-1)

class GraspVision(nn.Module):
    def __init__(self):
        super().__init__()
        self.features=nn.Sequential(nn.Conv2d(5,16,5,2,2),nn.SiLU(),nn.Conv2d(16,32,5,2,2),nn.SiLU(),
                                    nn.Conv2d(32,48,5,1,2),nn.SiLU(),nn.Conv2d(48,32,5,1,2),nn.SiLU())
        # The grasp location depends on the blade as well as the local handle.
        # This context stream covers roughly 285 input pixels, then combines
        # that wider view with precise local image features.
        self.context=nn.Sequential(nn.Conv2d(32,48,5,2,2),nn.SiLU(),nn.Conv2d(48,64,5,2,2),nn.SiLU(),
                                   nn.Conv2d(64,64,5,2,2),nn.SiLU(),nn.Conv2d(64,32,5,1,2),nn.SiLU())
        self.mix=nn.Sequential(nn.Conv2d(64,32,3,1,1),nn.SiLU())
        self.landmarks=nn.Conv2d(32,2,1)
        self.height=nn.Sequential(nn.Linear(72,48),nn.SiLU(),nn.Linear(48,2),nn.Tanh())

    def forward(self,im):
        features=self.features(im)
        context=F.interpolate(self.context(features),size=features.shape[-2:],mode='bilinear',align_corners=False)
        features=self.mix(torch.cat([features,context],1))
        logits=self.landmarks(features)
        xy,_=coordinates(logits)
        prob=logits.float().flatten(2).softmax(-1)
        local=torch.einsum('bkn,bcn->bkc',prob,features.float().flatten(2)).flatten(1)
        norm=(xy-xy.new_tensor([96.,96.]))/xy.new_tensor([447.,319.])*2-1
        # Explicit image-space position and observed depth/validity are sensor
        # inputs. Object pose, family, rest face and reset values are absent.
        sensor=F.grid_sample(im[:,3:5].float(),norm[:,:,None],align_corners=True).flatten(1)
        height=self.height(torch.cat([local,norm.flatten(1),sensor],1))*.015
        return logits,height
