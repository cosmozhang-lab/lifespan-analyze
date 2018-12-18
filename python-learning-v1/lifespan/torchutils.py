import torch

class OneHotTransform:
    def __init__(self, length):
        self.length = length
        self.src = torch.ones(length)
    def __call__(self, inputtensor):
        shape = list(inputtensor.shape)
        if len(shape) == 0 or inputtensor.shape[-1] != 1:
            shape = shape + [1]
            inputtensor = inputtensor.view(shape)
        shape[-1] = self.length
        shape = tuple(shape)
        dim = len(shape) - 1
        return torch.zeros(shape).scatter_(dim, inputtensor.type(torch.long), 1)
