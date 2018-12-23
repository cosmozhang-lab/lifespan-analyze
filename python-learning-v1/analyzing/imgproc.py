from learning.trainer import Trainer
from learning.discriminator import Discriminator
from learning.

class ImageProcessor:
    def __init__(self, from_path=None, model_path=None, device="cpu"):
        self.device = torch.device(device)
        self.discriminator = Discriminator()
        Trainer.load_model_params(self.discriminator, userconfig.model_path)
        self.discriminator.to(self.device)
    def fine_worms(image, bwlworms):
        for i in range(len(regionids)):
            rx,ry,rw,rh = tuple(regions[i,:])
            mw,mh = mp.marksize
            imw,imh = tuple(image.shape)
            if rw < mw: rx = min(imw-mw, max(0, int(rx-(mw-rw)/2)))
            if rh < mh: ry = min(imh-mh, max(0, int(ry-(mh-rh)/2)))
            image = torch.FloatTensor(image).to(self.device)
            bwlworms = torch.FloatTensor(bwlworms==int(regionids[i])).to(self.device)
            inputimg = torch.stack([image,bwlworms], dim=0)

