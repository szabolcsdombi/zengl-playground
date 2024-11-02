import pygame
import string

import zengl_playground


class Console:
    def __init__(self):
        self.visible = False
        self.line = ''
        self.history = []

    def toggle(self):
        self.visible = not self.visible

    def update(self):
        if not self.visible:
            return

        app = zengl_playground.get_app()
        app.font.write(10, 40, '# ' + self.line)
        for i, row in enumerate(self.history[::-1]):
            app.font.write(10, 40 + 28 * (1 + i), row)

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKQUOTE:
                self.toggle()

        if self.visible:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.line = self.line[:-1]

                if event.key == pygame.K_RETURN:
                    self.history.append('# ' + self.line)

                    try:
                        app = zengl_playground.get_app()
                        result = app.execute_command(self.line)
                        self.history.append('= ' + repr(result)[:100])

                    except Exception as e:
                        self.history.append('= ' + repr(e)[:100])

                    self.history = self.history[-16:]
                    self.line = ''

                if event.unicode in string.printable and event.unicode not in '\t\r\n`':
                    self.line += event.unicode
