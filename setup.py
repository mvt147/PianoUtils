from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='piano_utils',
    modules=['piano_utils'],
    version='0.1',
    description='Piano Utilities',
    author='Michael Van Treeck',
    author_email='michael.vantreeck@mq.edu.au',
    url='https://github.com/mvt147/PianoUtils',
    license='MIT',
    keywords=['piano', 'util', 'xml', 'json'],
    classifiers=[],
    install_requires=requirements,
)
