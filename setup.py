# DEPRECATED: This setup.py is deprecated and should not be used. Use pyproject.toml or other modern packaging tools instead.
from setuptools import setup, find_packages

setup(
    name="ir_support",
    version="1.1.0b",
    description="Python package including some classes & functions supporting the subject 41013 Industrial Robotics at UTS, along with the Robotics Toolbox for Python",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8,<3.12",
    packages=find_packages(include=["ir_support"]),
    install_requires=[
        "pandas>=2.0.3,<2.2.2",
        "trimesh>=4.0.0,<4.4.4",
        "plyfile>=1.0.1,<1.0.2",
        "keyboard>=0.13.5",
        "scikit-image>=0.21.0,<0.22.0",
        "more-itertools>=10.0.0,<10.4.0",
        "open3d>=0.18.0",
        "spatialmath-python==1.1.8",
        "matplotlib==3.7.2",
    ],
    url="https://github.com/H-M-Quang-Ngo/ir-support",
    author="Quang Ngo",
    author_email="quang.ngohominh@gmail.com",
)
