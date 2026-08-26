from setuptools import setup, find_packages

setup(
    name="telenet",
    version="3.0.0",
    packages=find_packages(),
    install_requires=["aiohttp>=3.9"],
    python_requires=">=3.9",
    author="Ali Jafari",
    author_email="thealiapi@gmail.com",
    description="TeleNet: Async Telegram Bot API framework",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: AsyncIO",
        "Topic :: Communications :: Chat",
    ],
)
