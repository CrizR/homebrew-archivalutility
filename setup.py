import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
    name='ArchivalUtility',
    version='1',
    scripts=['run'],
    author="Christopher Risley",
    author_email="risleychris@gmail.com",
    description="An archival utility package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/archival_utility/CrizR",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
