"""Image/proprioception recurrent pickup student, without object-state inputs."""
import torch
from torch import nn


class ImageEncoder(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(5, 16, 5, 2, 2), nn.SiLU(),
            nn.Conv2d(16, 24, 3, 2, 1), nn.SiLU(),
            nn.Conv2d(24, 32, 3, 2, 1), nn.SiLU(),
            nn.Conv2d(32, 16, 1))

    def forward(self, images):
        # Fixed head-camera crop includes all four calibrated board corners plus
        # margin. It never follows a ground-truth/detected object location.
        features = self.conv(images[..., 48:208, 48:272])
        n, c, h, w = features.shape
        probability = features.flatten(2).softmax(-1)
        yy, xx = torch.meshgrid(torch.linspace(-1, 1, h, device=images.device),
                                torch.linspace(-1, 1, w, device=images.device), indexing='ij')
        return torch.cat([(probability * xx.flatten()).sum(-1),
                          (probability * yy.flatten()).sum(-1),
                          features.mean((2, 3)), features.amax((2, 3))], dim=-1)


class VisionPickupPolicy(nn.Module):
    def __init__(self, mean, scale):
        super().__init__()
        self.encoder = ImageEncoder()
        self.register_buffer('mean', torch.as_tensor(mean, dtype=torch.float32))
        self.register_buffer('scale', torch.as_tensor(scale, dtype=torch.float32))
        self.register_buffer('action_scale', torch.tensor([.04] * 7 + [.02] * 6))
        self.recurrent = nn.GRU(64 * 2 + 13 * 4, 128, batch_first=True)
        self.action = nn.Sequential(nn.Linear(128, 64), nn.SiLU(), nn.Linear(64, 13), nn.Tanh())
        self.goal = nn.Sequential(nn.Linear(64, 64), nn.SiLU(), nn.Linear(64, 7))

    def forward(self, images, initial, q, qd, target, previous_action, hidden=None):
        batch, length = images.shape[:2]
        visual = self.encoder(images.flatten(0, 1)).reshape(batch, length, -1)
        memory = self.encoder(initial)
        inputs = torch.cat([visual, memory[:, None].expand(-1, length, -1),
                            (q - self.mean) / self.scale, qd,
                            (target - self.mean) / self.scale,
                            previous_action / self.action_scale], dim=-1)
        features, hidden = self.recurrent(inputs, hidden)
        return self.action(features), self.goal(memory), hidden


def image_tensor(rgb, depth, device):
    """RGB-D plus explicit validity; missing depth is never replaced with geometry."""
    rgb = torch.as_tensor(rgb.copy(), device=device).float().movedim(-1, -3) / 255.
    depth = torch.as_tensor(depth.astype('float32'), device=device)
    valid = torch.isfinite(depth) & (depth > 0.) & (depth < 3.)
    clean = torch.where(valid, depth.clamp(0., 3.) / 3., 0.)
    return torch.cat([rgb, clean.unsqueeze(-3), valid.float().unsqueeze(-3)], dim=-3)
