from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='piano_utils',
    packages=find_packages(exclude=["tests"]),
    version='0.1.1',
    description='Piano Utilities',
    author='Michael Van Treeck',
    author_email='michael.vantreeck@mq.edu.au',
    url='https://github.com/mvt147/PianoUtils',
    license='MIT',
    keywords=['piano', 'util', 'xml', 'json'],
    classifiers=[],
    install_requires=requirements,
)
