from setuptools import setup, find_packages

setup(
    name="pyfig",
    version="0.1.0",
    packages=find_packages(include=["pyfig", "pyfig.*"]),
    install_requires=[
        "pydantic>=2.0.0,<3.0.0"
    ],
)