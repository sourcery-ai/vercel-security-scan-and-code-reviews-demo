"""
Setup configuration for BlogHub application.
"""
from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="bloghub",
    version="1.2.0",
    description="A simple blog and content management system",
    author="BlogHub Team",
    author_email="team@bloghub.com",
    url="https://github.com/bloghub/bloghub",
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: Flask",
    ],
    entry_points={
        "console_scripts": [
            "bloghub=app:create_app",
        ],
    },
)
