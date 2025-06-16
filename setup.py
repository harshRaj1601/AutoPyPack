from setuptools import setup, find_packages

setup(
    name="autopylot",  # Keep lowercase for pip install and CLI
    version="1.0.0",
    description="Automatically installs missing Python libraries when running your code.",
    author="Harsh Jaiswal",
    author_email="harshrajjaiswal16012003@gmail.com",
    url="https://github.com/harshRaj1601/AutoPylot",  # Optional GitHub repo link
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'autopylot': ['mappings.json'],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        # Basic packages that AutoPylot itself needs
        "setuptools",
    ],
    entry_points={
        'console_scripts': [
            'autopylot=autopylot.cli:main',
        ],
    },
)
