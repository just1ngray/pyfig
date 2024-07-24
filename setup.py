from setuptools import setup, find_packages

def get_version() -> str:
    with open("pyfig/__init__.py", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("__version__"):
                return line.split("=", maxsplit=1)[1].strip(" '\"")
    raise ValueError("Version not found")

setup(
    name="pyfig",
    version=get_version(),
    author="Justin Gray",
    author_email="just1ngray@outlook.com",
    url="https://github.com/just1ngray/pyfig",
    description=" A simple, yet capable configuration library for Python",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    packages=find_packages(include=["pyfig", "pyfig.*"]),
    install_requires=[
        "pydantic>=2.0.0,<3.0.0"
    ],
)
