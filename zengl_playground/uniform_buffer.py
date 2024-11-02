import zengl


class UniformBuffer:
    def __init__(self):
        ctx = zengl.context()
        self.data = bytearray(1024)
        self.buffer = ctx.buffer(size=1024)
        ctx.includes['main_uniform_buffer'] = '''
            layout (std140) uniform Common {
                mat4 camera_matrix;
                mat4 inverse_camera_matrix;
                mat4 projection_matrix;
                mat4 view_matrix;
                vec4 camera_position;
                vec4 camera_target;
                vec2 screen_size;
                vec2 cursor_position;
                float time;
            };
        '''

    def update(self):
        self.buffer.write(self.data)
