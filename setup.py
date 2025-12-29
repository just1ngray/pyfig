from setuptools import setup, find_packages

setup(
    name="jpyfig",
    version="0.3.0",
    author="Justin Gray",
    author_email="just1ngray@outlook.com",
    url="https://github.com/just1ngray/pyfig",
    description="Configuration library built around pydantic",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    packages=find_packages(include=["pyfig", "pyfig.*"]),
    install_requires=[
        "pydantic>=2.0.0,<3.0.0"
    ],
)
