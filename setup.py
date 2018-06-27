import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="pydow",
    version="0.0.1",
    author="Gijs Wobben",
    author_email="andrewjcarter@gmail.com",
    description=(
        "An demonstration of how to create, document, and publish "
        "to the cheese shop a5 pypi.org."
    ),
    license="BSD",
    keywords="example documentation tutorial",
    url="http://packages.python.org/pydow",
    packages=["pydow", "tests"],
    tests_require=["pytest"],
    long_description=read("README.md"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)
