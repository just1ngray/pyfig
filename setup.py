import subprocess
from setuptools import setup, find_packages

def git_version() -> str:
    """
    If the latest commit is tagged, use that tag. Otherwise use the short commit hash.
    """
    try:
        # Get the latest tag, if available
        try:
            tag = subprocess.check_output(["git", "describe", "--tags", "--abbrev=0"]).strip().decode("utf-8")
        except subprocess.CalledProcessError:
            tag = None

        if tag:
            # Check if the current commit is exactly at the tag
            commit = subprocess.check_output(["git", "rev-parse", "HEAD"]).strip().decode("utf-8")
            tagged_commit = subprocess.check_output(["git", "rev-list", "-n", "1", tag]).strip().decode("utf-8")
            if commit == tagged_commit:
                return tag
            else:
                # Return commit hash if not exactly at a tag
                return "0.0." + subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).strip().decode("utf-8")
        else:
            # No tags found, return the commit hash
            return "0.0." + subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).strip().decode("utf-8")
    except subprocess.CalledProcessError:
        return "0.0.err"

setup(
    name="jpyfig",
    version=git_version(),
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
