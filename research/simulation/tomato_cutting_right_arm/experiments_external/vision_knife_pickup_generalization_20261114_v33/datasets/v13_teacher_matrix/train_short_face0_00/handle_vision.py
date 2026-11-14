"""Learn two handle landmarks from a fixed head-camera RGB-D workspace crop."""
import torch
from torch import nn
from vision_policy import image_tensor


class HandleVision(nn.Module):
    def __init__(self):
        super().__init__()
        self.network = nn.Sequential(
            nn.Conv2d(5,16,5,2,2),nn.SiLU(),
            nn.Conv2d(16,32,5,2,2),nn.SiLU(),
            nn.Conv2d(32,48,5,1,2),nn.SiLU(),
            nn.Conv2d(48,32,5,1,2),nn.SiLU(),
            nn.Conv2d(32,2,1))

    def forward(self, image):
        return self.network(image)


def prepare_image(rgb, depth, device):
    return image_tensor(rgb,depth,device)[...,48:208,48:272]


def coordinates(logits):
    n,c,h,w=logits.shape
    probability=logits.float().flatten(2).softmax(-1)
    yy,xx=torch.meshgrid(torch.arange(h,device=logits.device)*4.+48.,
                         torch.arange(w,device=logits.device)*4.+48.,indexing='ij')
    points=torch.stack([(probability*xx.flatten()).sum(-1),(probability*yy.flatten()).sum(-1)],-1)
    return points,probability.amax(-1)
