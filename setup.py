from setuptools import setup, find_packages

setup(
    name="mlforge",
    version="1.0.0",
    description="AI-powered ML project scaffolding CLI",
    author="ML SMITHS — OIST Bhopal",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "requests>=2.31",
    ],
    entry_points={
        "console_scripts": [
            # After `pip install -e .`, users can run `mlforge` from anywhere
            "mlforge=mlforge.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
