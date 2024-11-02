import os
import struct

import pygame
import zengl

import zengl_playground


class CursorAsset:
    def __init__(self, name, filename, offset, index):
        self.name = name
        self.filename = filename
        self.offset = offset
        self.index = index


CURSORS = [
    CursorAsset('cursor', 'cursor_none.png', (8, 4), 0),
    CursorAsset('hand', 'hand_point.png', (8, 4), 1),
    CursorAsset('pointer', 'pointer_c.png', (4, 4), 2),
    CursorAsset('crosshair', 'target_a.png', (16, 16), 3),
    CursorAsset('dot', 'dot_large.png', (16, 16), 4),
    CursorAsset('bracket', 'bracket_a_vertical.png', (16, 16), 5),
    CursorAsset('hourglass', 'busy_hourglass_outline.png', (16, 16), 6),
    CursorAsset('disabled', 'disabled.png', (16, 16), 7),
    CursorAsset('picker', 'drawing_picker.png', (6, 6), 8),
    CursorAsset('hand_closed', 'hand_closed.png', (16, 16), 9),
    CursorAsset('hand_open', 'hand_open.png', (16, 16), 10),
    CursorAsset('lock', 'lock.png', (16, 16), 11),
    CursorAsset('unlock', 'lock_unlocked.png', (16, 16), 12),
    CursorAsset('eye', 'look_c.png', (16, 16), 13),
    CursorAsset('message', 'message_dots_square.png', (16, 32), 14),
    CursorAsset('move', 'resize_b_cross.png', (16, 16), 15),
    CursorAsset('resize', 'resize_b_cross_diagonal.png', (16, 16), 16),
    CursorAsset('zoom_in', 'zoom_in.png', (12, 12), 17),
    CursorAsset('zoom_out', 'zoom_out.png', (12, 12), 18),
    CursorAsset('steps', 'steps.png', (16, 16), 19),
    CursorAsset('bucket', 'drawing_bucket.png', (6, 16), 20),
    CursorAsset('rotate_left', 'rotate_ccw.png', (16, 16), 21),
    CursorAsset('rotate_right', 'rotate_cw.png', (16, 16), 22),
]


def load_texture(filename):
    filename = os.path.normpath(os.path.join(__file__, '../../resources/cursors/', filename))
    img = pygame.image.load(filename)
    pixels = pygame.image.tobytes(img, 'RGBA')
    return pixels


class Cursor:
    def __init__(self):
        ctx = zengl.context()
        app = zengl_playground.get_app()

        texures = [load_texture(asset.filename) for asset in CURSORS]
        self.texture = ctx.image((32, 32), 'rgba8unorm', b''.join(texures), array=len(texures))
        self.lookup = {asset.name: asset for asset in CURSORS}

        self.pipeline = ctx.pipeline(
            vertex_shader='''
                #version 330 core

                #include "main_uniform_buffer"

                uniform vec2 cursor_offset;

                vec2 vertices[4] = vec2[](
                    vec2(0.0, 0.0),
                    vec2(0.0, 1.0),
                    vec2(1.0, 0.0),
                    vec2(1.0, 1.0)
                );

                out vec2 uv;

                void main() {
                    vec2 vertex = cursor_position + (vertices[gl_VertexID] * 32.0 - cursor_offset);
                    vertex.y = screen_size.y - vertex.y - 1.0;
                    gl_Position = vec4(vertex / screen_size * 2.0 - 1.0, 0.0, 1.0);
                    uv = vertices[gl_VertexID];
                }
            ''',
            fragment_shader='''
                #version 330 core

                uniform sampler2DArray Texture;
                uniform float cursor_index;

                in vec2 uv;

                layout (location = 0) out vec4 out_color;

                void main() {
                    out_color = texture(Texture, vec3(uv, cursor_index));
                }
            ''',
            layout=[
                {
                    'name': 'Common',
                    'binding': 0,
                },
                {
                    'name': 'Texture',
                    'binding': 0,
                },
            ],
            resources=[
                {
                    'type': 'uniform_buffer',
                    'binding': 0,
                    'buffer': app.uniform_buffer.buffer,
                },
                {
                    'type': 'sampler',
                    'binding': 0,
                    'image': self.texture,
                    'wrap_x': 'clamp_to_edge',
                    'wrap_y': 'clamp_to_edge',
                    'min_filter': 'nearest',
                    'mag_filter': 'nearest',
                },
            ],
            uniforms={
                'cursor_offset': [0.0, 0.0],
                'cursor_index': 0,
            },
            blend={
                'enable': True,
                'src_color': 'src_alpha',
                'dst_color': 'one_minus_src_alpha',
            },
            framebuffer=[app.framebuffer.image],
            topology='triangle_strip',
            vertex_count=4,
        )
        self.set_cursor('cursor')

    def set_cursor(self, name: str):
        asset = self.lookup[name]
        self.pipeline.uniforms['cursor_index'][:] = struct.pack('f', asset.index)
        self.pipeline.uniforms['cursor_offset'][:] = struct.pack('2f', *asset.offset)

    def render(self):
        self.pipeline.render()
