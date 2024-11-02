from setuptools import setup

setup(
    name='zengl-playground',
    packages=['zengl_playground', 'zengl_playground.renderers', 'zengl_playground.resources'],
    package_data={'zengl_playground.resources': ['**/*']},
    include_package_data=True,
    install_requires=['pygame-ce', 'pyglm', 'zengl-extras', 'zengl'],
)
