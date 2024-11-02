from typing import Tuple

import zengl


class Framebuffer:
    def __init__(self, size: Tuple[int, int]):
        self.size = size
        ctx = zengl.context()
        self.image = ctx.image(self.size, 'rgba8unorm')
        self.depth = ctx.image(self.size, 'depth24plus')
        self.framebuffer = [self.image, self.depth]

    def clear(self):
        self.image.clear()
        self.depth.clear()

    def blit(self):
        self.image.blit()
