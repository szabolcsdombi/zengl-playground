import json
import os
import struct

import pygame
import zengl

import zengl_playground


def make_atlas(size, filename: str, font_size: int):
    font_size = 24
    font = pygame.font.Font(filename, font_size)
    with open(filename.replace('.ttf', '.json')) as f:
        characters = json.loads(f.read())

    glyph_size = font.size('A')
    advance = font.size('AA')[0] - font.size('A')[0]
    glyph_width, glyph_height = glyph_size

    def make_glyph(c):
        glyph = pygame.Surface((glyph_width + 4, glyph_height + 4), pygame.SRCALPHA)
        try:
            char = font.render(chr(c), True, (255, 255, 255))
        except:
            return glyph
        for ox, oy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            glyph.blit(char, (ox + 2, oy + 2))
        glyph.fill((0, 0, 0, 90), special_flags=pygame.BLEND_RGBA_MULT)
        glyph.blit(char, (2, 2))
        return glyph

    lookup = {}
    atlas = pygame.Surface(size, pygame.SRCALPHA)
    for i, c in enumerate(characters):
        row = atlas.width // (glyph_width + 4)
        x = i % row * (glyph_width + 4)
        y = i // row * (glyph_height + 4)
        atlas.blit(make_glyph(c), (x, y))
        lookup[c] = x + 2, y + 2

    return lookup, glyph_size, advance, atlas


class Font:
    def __init__(self):
        filename = os.path.normpath(os.path.join(__file__, '../../resources/roboto-mono/roboto-mono.ttf'))
        lookup, glyph_size, advance, atlas = make_atlas((1024, 1024), filename, 24)
        self.lookup = lookup
        self.advance = advance

        ctx = zengl.context()
        app = zengl_playground.get_app()

        self.texture = ctx.image(atlas.size, 'rgba8unorm', pygame.image.tobytes(atlas, 'RGBA'))

        self.data = bytearray(1048576)
        self.data_size = 0

        self.buffer = ctx.buffer(self.data, access='dynamic_draw')

        self.pipeline = ctx.pipeline(
            vertex_shader='''
                #version 330 core

                #include "main_uniform_buffer"

                vec2 vertices[4] = vec2[](
                    vec2(0.0, 0.0),
                    vec2(0.0, 1.0),
                    vec2(1.0, 0.0),
                    vec2(1.0, 1.0)
                );

                uniform vec2 glyph_size;
                uniform vec2 atlas_size;

                layout (location = 0) in vec2 in_position;
                layout (location = 1) in vec2 in_offset;

                out vec2 v_texcoord;

                void main() {
                    v_texcoord = (in_offset + vertices[gl_VertexID] * glyph_size) / atlas_size;
                    vec2 vertex = in_position + vertices[gl_VertexID] * glyph_size * vec2(1.0, -1.0);
                    gl_Position = vec4(vertex / screen_size * 2.0 - 1.0, 0.0, 1.0);
                }
            ''',
            fragment_shader='''
                #version 330 core

                in vec2 v_texcoord;

                uniform sampler2D Texture;

                layout (location = 0) out vec4 out_color;

                void main() {
                    out_color = texture(Texture, v_texcoord);
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
                'glyph_size': glyph_size,
                'atlas_size': atlas.size,
            },
            blend={
                'enable': True,
                'src_color': 'src_alpha',
                'dst_color': 'one_minus_src_alpha',
            },
            framebuffer=[app.framebuffer.image],
            topology='triangle_strip',
            vertex_buffers=zengl.bind(self.buffer, '2f 2f /i', 0, 1),
            vertex_count=4,
        )

    def write(self, x, y, text):
        for i in range(len(text)):
            offset = self.lookup[ord(text[i])]
            self.data[self.data_size:self.data_size + 16] = struct.pack('4f', x + i * self.advance, y, *offset)
            self.data_size += 16

    def render(self):
        self.buffer.write(memoryview(self.data)[:self.data_size])
        self.pipeline.instance_count = self.data_size // 16
        self.pipeline.render()
        self.data_size = 0
