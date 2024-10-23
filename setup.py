"""
Setup configuration for Level42 Framework.

A lightweight Python framework for building autonomous AI agents that can pay for tools,
APIs, and other agents in real-time using L42 micropayments.
"""

from setuptools import setup, find_packages

# Read README for long description
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "A lightweight Python framework for building autonomous AI agents with micropayment capabilities."

# Read version from package
def get_version():
    """Get version from package __init__.py"""
    import os
    import re
    
    here = os.path.abspath(os.path.dirname(__file__))
    version_file = os.path.join(here, "level42", "__init__.py")
    
    with open(version_file, "r", encoding="utf-8") as f:
        version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", f.read(), re.M)
        if version_match:
            return version_match.group(1)
    
    raise RuntimeError("Unable to find version string.")

version = get_version()

setup(
    name="level42",
    version="0.2.0",
    author="Level42 Framework Team",
    author_email="team@level42.dev",
    description="A lightweight Python framework for building autonomous AI agents with micropayment capabilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tjelz/level42",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Office/Business :: Financial",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
        "web3>=6.0.0",
        "langchain-core>=0.1.0",
        "cryptography>=3.4.8",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "solana": [
            "solana>=0.30.0",
            "solders>=0.18.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=1.0.0",
            "coverage>=6.0.0",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "myst-parser>=0.18.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "level42=level42.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "level42": ["py.typed"],
    },
    keywords=[
        "ai",
        "agents",
        "micropayments",
        "blockchain",
        "cryptocurrency",
        "api",
        "automation",
        "web3",
        "usdc",
        "base",
        "level42",
        "l42",
    ],
    project_urls={
        "Bug Reports": "https://github.com/tjelz/level42/issues",
        "Source": "https://github.com/tjelz/level42",
        "Documentation": "https://docs.level42.dev",
    },
)