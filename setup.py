import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PhylogicReviewer",
    version="0.0.1",
    author="Conor Messer",
    author_email="cmesser@broadinstitute.org",
    description="A tool to review Phylogic solutions using JupyterReviewer Plotly dashboards",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/getzlab/PhylogicReviewer",
    project_urls={
        "Bug Tracker": "https://github.com/getzlab/PhylogicReviewer/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "."},
    packages=setuptools.find_packages(where="."),
    python_requires=">=3.6",
    install_requires = ['JupyterReviewer==0.0.2',
                        'firecloud-dalmatian',
                       ]
)   

