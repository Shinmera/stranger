import pathlib
from setuptools import setup

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.mess").read_text()

setup(
    name='stranger',
    version='0.1',
    description='A discord bot.',
    long_description=README,
    license='zlib',
    author='Nicolas Hafner',
    author_email='shinmera@tymoon.eu',
    keywords=['chat','discord']
    packages=['stranger'],
    classifiers=[
        "License :: OSI Approved :: zlib/libpng License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Development Status :: 5 - Production/Stable",
        "Topic :: Internet"
    ],
    entry_points={
        "console_scripts": [
            "stranger=stranger.__main__:main",
        ]
    },
)
