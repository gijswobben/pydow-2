import os
from setuptools import setup
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
    packages=[
        "pydow",
        "pydow.components",
        "pydow.components.button",
        "pydow.components.input",
        "pydow.core",
        "pydow.events",
        "pydow.plugins",
        "pydow.router",
        "pydow.router.link",
        "pydow.router.router",
        "pydow.store"
    ],
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
