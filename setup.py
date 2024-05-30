import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PhylogicNDTReviewer",
    version="1.0.0",
    author="Conor Messer",
    author_email="cmesser@broadinstitute.org",
    description="A tool to review PhylogicNDT solutions using JupyterReviewer Plotly dashboards",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/getzlab/PhylogicNDTReviewer",
    project_urls={
        "Bug Tracker": "https://github.com/getzlab/PhylogicNDTReviewer/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "."},
    packages=setuptools.find_packages(where="."),
    python_requires=">=3.8", # last tested version: 3.9
    install_requires = ['AnnoMate>=1.0.0',
                        'firecloud-dalmatian',
                       ]
)   

