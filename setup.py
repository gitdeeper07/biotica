"""BIOTICA - Ecosystem Resilience Framework"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="biotica-ecosystem",  # نفس الاسم المستخدم في الرفع
    version="1.0.1",
    author="Samir Baladi",
    author_email="gitdeeper@gmail.com",
    description="BIOTICA: Bio-Geochemical Framework for Ecosystem Resilience Assessment",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/biotica/biotica",
    project_urls={
        "Bug Tracker": "https://gitlab.com/biotica/biotica/-/issues",
        "Documentation": "https://biotica.readthedocs.io",
        "Source Code": "https://gitlab.com/biotica/biotica",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Ecology",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
    ],
    keywords="ecosystem resilience environmental-monitoring biodiversity climate-change conservation ecology",
)
