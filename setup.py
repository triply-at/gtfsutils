from setuptools import setup


with open("gtfsutils/__init__.py") as f:
    for line in f:
        if "__version__" in line:
            version = line.split("=")[1].strip().strip('"').strip("'")
            continue

setup(
    name='gtfsutils',
    version=version,
    url='https://github.com/triply-at/gtfsutils',
    author='Nikolai Janakiev',
    author_email='n.janakiev@triply.at',
    description='gtfsutils',
    platforms='any',
    packages=['gtfsutils'],
    install_requires=[],
    entry_points={
        "console_scripts": [
            "gtfsutils = gtfsutils.__main__:main"
        ]
    }
)
