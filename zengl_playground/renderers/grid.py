import zengl

import zengl_playground


class Grid:
    def __init__(self):
        ctx = zengl.context()
        app = zengl_playground.get_app()
        self.pipeline = ctx.pipeline(
            vertex_shader='''
                #version 330 core

                layout (std140) uniform Common {
                    mat4 camera_matrix;
                };

                const int N = 17;

                void main() {
                    float size = 5.0;
                    float u = float(gl_VertexID % 2);
                    float v = float(gl_VertexID / 2 % N) / float(N - 1);
                    vec2 vertex = (vec2(u, v) - 0.5) * size;
                    if (gl_VertexID > N * 2) {
                        vertex = vertex.yx;
                    }
                    gl_Position = camera_matrix * vec4(vertex, 0.0, 1.0);
                }
            ''',
            fragment_shader='''
                #version 330 core

                layout (location = 0) out vec4 out_color;

                uniform vec3 Color;

                void main() {
                    out_color = vec4(Color, 1.0);
                }
            ''',
            layout=[
                {
                    'name': 'Common',
                    'binding': 0,
                },
            ],
            resources=[
                {
                    'type': 'uniform_buffer',
                    'binding': 0,
                    'buffer': app.uniform_buffer.buffer,
                },
            ],
            uniforms={
                'Color': [0.1, 0.1, 0.1],
            },
            framebuffer=app.framebuffer.framebuffer,
            topology='lines',
            vertex_count=17 * 4,
        )

    def render(self):
        self.pipeline.render()
