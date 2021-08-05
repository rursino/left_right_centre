import os
from setuptools import setup 
from left_right_centre import __version__


SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
BIN_FILES = [
    'bin/%s' % f for f in os.listdir(os.path.join(SCRIPT_DIR, 'bin'))
    if f[0] != '.'
]


setup(
    name='left_right_centre',
    version=__version__,
    description='A simple game of Left, Right, Centre with ability to perform simulations.',
    author='Ross Ursino',
    packages=['left_right_centre'],
    scripts=BIN_FILES
)
