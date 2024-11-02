import zengl

import zengl_playground


class Background:
    def __init__(self):
        ctx = zengl.context()
        app = zengl_playground.get_app()
        self.pipeline = ctx.pipeline(
            vertex_shader='''
                #version 330 core

                vec2 vertices[3] = vec2[](
                    vec2(-1.0, -1.0),
                    vec2(3.0, -1.0),
                    vec2(-1.0, 3.0)
                );

                out vec2 v_vertex;

                void main() {
                    gl_Position = vec4(vertices[gl_VertexID], 0.0, 1.0);
                    v_vertex = vertices[gl_VertexID];
                }
            ''',
            fragment_shader='''
                #version 330 core

                #include "main_uniform_buffer"

                in vec2 v_vertex;

                layout (location = 0) out vec4 out_color;

                void main() {
                    vec4 position_temp = inverse_camera_matrix * vec4(v_vertex, -1.0, 1.0);
                    vec4 target_temp = inverse_camera_matrix * vec4(v_vertex, 1.0, 1.0);
                    vec3 position = position_temp.xyz / position_temp.w;
                    vec3 target = target_temp.xyz / target_temp.w;
                    vec3 direction = normalize(target - position);

                    vec3 color;
                    if (direction.z > 0.0) {
                        vec3 color1 = vec3(1.0, 1.0, 1.0);
                        vec3 color2 = vec3(0.1, 0.5, 0.9);
                        color = mix(color1, color2, pow(direction.z, 0.4));
                    } else {
                        vec3 color1 = vec3(1.0, 1.0, 1.0);
                        vec3 color2 = vec3(0.2, 0.2, 0.2);
                        color = mix(color1, color2, pow(-direction.z, 0.1));
                    }

                    out_color = vec4(color, 1.0);
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
            framebuffer=[app.framebuffer.image],
            topology='triangles',
            vertex_count=3,
        )

    def render(self):
        self.pipeline.render()
