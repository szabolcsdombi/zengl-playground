from zengl_playground import playground


def run(cls):
    app = playground.Playground()
    app.handler = cls()
    app.run()


def get_app():
    return playground.app
