import os
import struct
import sys

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'

import pygame
import zengl
import zengl_extras

from zengl_playground import camera, console, framebuffer, uniform_buffer
from zengl_playground.renderers import background, cursor, font, grid, logo


class Handler:
    def render(self): ...
    def on_load(self): ...
    def on_exit(self): ...
    def on_update(self): ...
    def on_keydown(self, key): ...
    def on_keyup(self, key): ...
    def on_mousemove(self, pos): ...
    def execute_command(self, line): ...


class Playground:
    handler: Handler

    def __init__(self):
        globals()['app'] = self
        zengl_extras.init()

        pygame.init()
        pygame.display.set_mode((1280, 720), flags=pygame.OPENGL | pygame.DOUBLEBUF, vsync=True)
        pygame.display.set_caption('ZenGL Playground')
        pygame.display.set_icon(logo.render_logo())
        pygame.mouse.set_visible(False)

        self.clock = pygame.Clock()
        self.fps = 0

        self.ctx = zengl.context()
        self.size = pygame.display.get_window_size()

        self.framebuffer = framebuffer.Framebuffer(self.size)
        self.uniform_buffer = uniform_buffer.UniformBuffer()
        self.camera = camera.Camera()

        self.background = background.Background()
        self.grid = grid.Grid()
        self.font = font.Font()
        self.cursor = cursor.Cursor()
        self.console = console.Console()
        self.handler = None

    def execute_command(self, line: str):
        if hasattr(self.handler, 'execute_command'):
            return self.handler.execute_command(line)
        scope = {'self': self.handler}
        return eval(line, globals=scope, locals=scope)

    def setup_moderngl(self, ctx):
        ctx._screen = ctx.detect_framebuffer(zengl.inspect(self.grid.pipeline)['framebuffer'])
        ctx.includes['main_uniform_buffer'] = self.ctx.includes['main_uniform_buffer']

    def run(self):
        if hasattr(self.handler, 'on_load'):
            self.handler.on_load()

        while True:
            for event in pygame.event.get():
                if self.console.handle_event(event):
                    continue

                if self.camera.handle_event(event):
                    continue

                if event.type == pygame.MOUSEMOTION:
                    if hasattr(self.handler, 'on_mousemove'):
                        self.handler.on_mousemove(event.pos)

                if event.type == pygame.KEYDOWN:
                    if hasattr(self.handler, 'on_keydown'):
                        self.handler.on_keydown(event.key)

                if event.type == pygame.KEYUP:
                    if hasattr(self.handler, 'on_keyup'):
                        self.handler.on_keyup(event.key)

                if event.type == pygame.QUIT:
                    if hasattr(self.handler, 'on_exit'):
                        self.handler.on_exit()

                    pygame.quit()
                    sys.exit()

            if hasattr(self.handler, 'on_update'):
                self.handler.on_update()

            now = pygame.time.get_ticks() / 1000.0
            mouse = pygame.mouse.get_pos()

            self.uniform_buffer.data[0:288] = self.camera.pack()
            self.uniform_buffer.data[288:308] = struct.pack('5f', *self.size, *mouse, now)

            self.console.update()

            self.fps = self.fps * 0.97 + self.clock.get_fps() * 0.03
            self.font.write(10, self.size[1] - 10, f'{self.fps:3.0f}fps')

            self.ctx.new_frame()
            self.uniform_buffer.update()
            self.framebuffer.clear()

            self.background.render()
            self.grid.render()
            self.handler.render()
            self.font.render()

            if pygame.mouse.get_focused():
                self.cursor.render()

            self.framebuffer.blit()
            self.ctx.end_frame()

            pygame.display.flip()
            self.clock.tick()


app: Playground = None
