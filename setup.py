import os
import re
from setuptools import setup, find_packages


def get_version():
    # Read version from racoon_clip/racoon_clip/__init__.py
    version_file = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "racoon_clip",
        "__init__.py",
    )
    with open(version_file, "r") as f:
        content = f.read()
    version_match = re.search(r'__version__\s*=\s*[\'"]([^\'"]+)[\'"]', content)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string in __init__.py")
    

def get_description():
    with open("README.md", "r") as fh:
        long_description = fh.read()
    return long_description


def get_data_files():
    data_files = [(".", ["README.md"])]
    return data_files


CLASSIFIERS = [
    "Environment :: Console",
    "Environment :: MacOS X",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: Other/Proprietary License",
    "Natural Language :: English",
    "Operating System :: POSIX :: Linux",
    "Operating System :: MacOS :: MacOS X",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Topic :: Scientific/Engineering :: Bio-Informatics",
]

setup(
    name="racoon_clip",
    packages=find_packages(),
    url="",
    python_requires="==3.9.0",
    description="Snakemake-powered commandline tool to obtain single-nucleotide crosslinks from i/eCLIP data.",
    long_description=get_description(),
    long_description_content_type="text/markdown",
    version=get_version(),
    author="Melina Klostermann",
    author_email="melinaklostermann@googlemail.com",
    data_files=get_data_files(),
    py_modules=["racoon_clip"],
    install_requires=[
        "snakemake==7.22",
        "pyyaml>=6.0",
        "Click>=8.1.3",
        "pulp==2.7.0"
    ],
    entry_points={
        "console_scripts": [
            "racoon_clip=racoon_clip.__main__:main"
        ]
    },
    include_package_data=True,
)
