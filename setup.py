import setuptools
from pathlib import Path

work_dir = Path(__file__).parent
long_description = (work_dir / "README.md").read_text()


setuptools.setup(

    name="implexus",
    version="0.1.0",
    author="Eryk J.",
    url="https://github.com/erykjj/implexus",

    description="Generate WireGuard configs based on a network outline",
    long_description=long_description,
    long_description_content_type="text/markdown",

    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=[ 'argparse', 'os', 'pyyaml', 'subprocess']

)