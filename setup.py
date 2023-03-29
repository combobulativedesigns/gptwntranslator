# setup.py

from setuptools import setup, find_packages

with open("README.md", "r") as readme_file:
    long_description = readme_file.read()

with open("requirements.txt", "r") as requirements_file:
    requirements = requirements_file.read().splitlines()

setup(
    name="GPTWebNovelTranslator",
    version="0.1.0",
    author="Rodrigo S. Jauregui",
    author_email="ro.sjda42@gmail.com",
    description="A web novel translator using gpt-3.5-turbo and gpt-4",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/CombobulativeDesigns/GPTWebNovelTranslator",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Text Processing :: Linguistic",
    ],
    entry_points={
        "console_scripts": [
            "gptwntranslator = main:main",
        ],
    },
    python_requires=">=3.10",
)

        

