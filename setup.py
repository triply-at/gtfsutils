from setuptools import setup
from pathlib import Path


# Version number
with open("gtfsutils/__init__.py") as f:
    for line in f:
        if "__version__" in line:
            version = line.split("=")[1].strip().strip('"').strip("'")
            continue

# The text of the README file
this_directory = Path(__file__).absolute().parent
with open(this_directory / "README.md") as f:
    README = f.read()

# Requirements
try:
    this_directory = Path(__file__).absolute().parent
    with open((this_directory / 'requirements.txt'), encoding='utf-8') as f:
        requirements = f.readlines()
    requirements = [line.strip() for line in requirements]
except FileNotFoundError:
    requirements = []

setup(
    name='gtfsutils',
    version=version,
    url='https://github.com/triply-at/gtfsutils',
    author='Nikolai Janakiev',
    author_email='n.janakiev@triply.at',
    description=README,
    long_description_content_type='text/markdown',
    license="MIT",
    platforms='any',
    packages=['gtfsutils'],
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "gtfsutils = gtfsutils.__main__:main"
        ]
    }
)
