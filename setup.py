from setuptools import find_packages, setup

with open("app/README.md", "r") as f:
    long_description = f.read()

setup(
    name="getRoutersConfig",
    version="0.0.5",
    description="get Cisco routers configuration as Json",
    package_dir={"": "app"},
    packages=find_packages(where="app"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DanielRicklin/getRoutersConfig",
    author="DanielRicklin",
    author_email="ricklin.daniel@outlook.fr",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    install_requires=["netmiko >= 4.1.2","pysnmp>=4.4.12"],
    extras_require={
        "dev": ["twine >= 4.0.2"],
    },
    python_requires=">=3.7",
)

#python setup.py bdist_wheel sdist
#python -m twine check dist/*
#python -m twine upload dist/*

#Test the code
#pip install .
#python main.py
