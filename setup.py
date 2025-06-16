from setuptools import setup, find_packages

# Read the README.md file for the long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="autopypack",  # Keep lowercase for pip install and CLI
    version="1.0.1",
    description="Automatically installs missing Python libraries when running your code.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Harsh Jaiswal",
    author_email="harshrajjaiswal16012003@gmail.com",
    url="https://github.com/harshRaj1601/AutoPyPack",  # Optional GitHub repo link
    packages=find_packages(),
    include_package_data=True,
    package_data={        'autopypack': ['mappings.json'],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        # Basic packages that AutoPyPack itself needs
        "setuptools",
    ],    entry_points={
        'console_scripts': [
            'autopypack=AutoPyPack.autopypack.cli:main',
        ],
    },
)
