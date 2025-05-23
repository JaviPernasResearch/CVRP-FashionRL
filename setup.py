from setuptools import setup, find_packages

setup(
    name="fashion_reverse_logistics",
    version="1.0.0",
    description="Fashion Reverse Logistics CVRP Solver",
    author="Javier Pernas",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "matplotlib",
        "gurobipy",
        "ortools",
        "pandas",
        "tkinter",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)