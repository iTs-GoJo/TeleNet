from setuptools import setup, find_packages
setup(
    name="telenet",
    version="2.7.0",
    packages=find_packages(),
    install_requires=["aiohttp>=3.9"],
)