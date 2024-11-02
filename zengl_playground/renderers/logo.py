import pygame
import zengl


def render_logo():
    ctx = zengl.context()
    image = ctx.image((32, 32), 'rgba8unorm')
    pipeline = ctx.pipeline(
        vertex_shader='''
            #version 330 core

            vec2 vertices[3] = vec2[](
                vec2(0.0, -0.8),
                vec2(-0.866, 0.7),
                vec2(0.866, 0.7)
            );

            vec3 colors[3] = vec3[](
                vec3(1.0, 0.0, 0.0),
                vec3(0.0, 1.0, 0.0),
                vec3(0.0, 0.0, 1.0)
            );

            out vec3 v_color;

            void main() {
                gl_Position = vec4(vertices[gl_VertexID], 0.0, 1.0);
                v_color = colors[gl_VertexID];
            }
        ''',
        fragment_shader='''
            #version 330 core

            in vec3 v_color;

            layout (location = 0) out vec4 out_color;

            void main() {
                out_color = vec4(v_color, 1.0);
                out_color.rgb = pow(out_color.rgb, vec3(1.0 / 2.2));
            }
        ''',
        framebuffer=[image],
        topology='triangles',
        vertex_count=3,
    )

    image.clear()
    pipeline.render()
    logo = pygame.image.frombuffer(image.read(), image.size, 'RGBA')
    ctx.release(pipeline)
    ctx.release(image)

    return logo
