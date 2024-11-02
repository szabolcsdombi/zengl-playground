import struct

import glm
import pygame

import zengl_playground

camera_struct = struct.Struct('64s64s64s64s3f4x3f4x')


class Camera:
    def __init__(self):
        app = zengl_playground.get_app()
        self.aspect = app.framebuffer.size[0] / app.framebuffer.size[1]
        self.position = glm.vec3(4.0, 3.0, 2.0)
        self.target = glm.vec3(0.0, 0.0, 0.0)

    def rotate(self, mouse_x, mouse_y):
        direction = self.position - self.target
        length = glm.length(direction)
        x = glm.atan2(direction.y, direction.x)
        y = glm.atan2(direction.z, glm.sqrt(direction.x ** 2 + direction.y ** 2))
        x = x - mouse_x * 0.01
        y = glm.clamp(y + mouse_y * 0.01, -glm.pi() / 2.0 + 0.01, glm.pi() / 2.0 - 0.01)
        direction = glm.vec3(glm.cos(y) * glm.cos(x), glm.cos(y) * glm.sin(x), glm.sin(y))
        self.position = self.target + direction * length

    def pan(self, mouse_x, mouse_y):
        direction = self.position - self.target
        up = glm.vec3(0.0, 0.0, 1.0)
        sideways = glm.normalize(glm.cross(direction, up))
        up = glm.normalize(glm.cross(sideways, direction))
        move = sideways * mouse_x * 0.01 + up * mouse_y * 0.01
        self.position += move
        self.target += move

    def zoom(self, delta):
        direction = self.position - self.target
        length = glm.length(direction) * 0.9 ** delta
        self.position = self.target + glm.normalize(direction) * length

    def pack(self):
        projection = glm.perspective(glm.radians(70.0), self.aspect, 0.1, 100.0)
        view = glm.lookAt(self.position, self.target, glm.vec3(0.0, 0.0, 1.0))
        mvp = projection * view
        inverse_mvp = glm.inverse(mvp)
        return camera_struct.pack(
            mvp.to_bytes(),
            inverse_mvp.to_bytes(),
            projection.to_bytes(),
            view.to_bytes(),
            *self.position,
            *self.target,
        )

    def handle_event(self, event: pygame.event.Event):
        shift_down = pygame.key.get_mods() & pygame.KMOD_SHIFT
        middle_mouse_down = pygame.mouse.get_pressed()[1]

        if event.type == pygame.MOUSEMOTION and middle_mouse_down:
            if shift_down:
                self.pan(event.rel[0], event.rel[1])
            else:
                self.rotate(event.rel[0], event.rel[1])

        if event.type == pygame.MOUSEWHEEL:
            self.zoom(event.y)
