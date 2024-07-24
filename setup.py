import time
import subprocess
from setuptools import setup, find_packages

def _last_git_tag() -> str:
    try:
        return subprocess.check_output(["git", "describe", "--tags", "--abbrev=0"]).strip().decode("utf-8")
    except subprocess.CalledProcessError:
        return "0.1.0"

def git_version() -> str:
    """
    If the latest commit is tagged, use that tag. Otherwise use the short commit hash.
    """
    try:
        tag = _last_git_tag()

        # Check if the current commit is exactly at the tag
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"]).strip().decode("utf-8")
        try:
            tagged_commit = subprocess.check_output(["git", "rev-list", "-n", "1", tag]).strip().decode("utf-8")
            if commit == tagged_commit:
                return tag
        except subprocess.CalledProcessError:
            pass

        return f"0.1.{int(commit[:7], 16)}"
    except subprocess.CalledProcessError:
        return f"0.1.{int(time.time())}"

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
