from setuptools import setup, find_packages
from os import path

from version import __version__

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'docs/README.rst')) as f:
    long_description = f.read()

with open(path.join(here, 'requirements.txt')) as f:
    requirements = [
        line
        for line in f
    ]


setup(
    name='fbcm',
    version=__version__,
    description="Football Championship Manager",
    long_description=long_description,
    author="Santos Gallegos",
    author_email="santos_g@outlook.com",
    license='MIT',
    packages=find_packages(exclude=['docs', 'tests']),
    include_package_data=True,
    install_requires=requirements,
)
