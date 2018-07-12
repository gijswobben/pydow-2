import os
from setuptools import setup
from setuptools import find_packages
from version import __version__


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="pydow",
    version=__version__,
    author="Gijs Wobben",
    author_email="gijswobben@gmail.com",
    description=(
        "virtual DOM in the shadow."
    ),
    license="MIT",
    keywords="example documentation tutorial",
    url="http://packages.python.org/pydow",
    packages=find_packages(),
    install_requires=[
        "flask",
        "flask-socketio"
    ],
    tests_require=["pytest"],
    long_description=read("README.md"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities"
    ],
)
