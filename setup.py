# setup.py

from setuptools import setup, find_packages

with open("README.md", "r") as readme_file:
    long_description = readme_file.read()

setup(
    name="gpt-wn-translator",
    version="0.1.0",
    author="Rodrigo S. Jauregui",
    author_email="ro.sjda42@gmail.com",
    description="A web novel translator using gpt-3.5-turbo and gpt-4",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/CombobulativeDesigns/GPTWebNovelTranslator",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=[
        "beautifulsoup4==4.12.0",
        "Janome==0.4.2",
        "openai==0.27.2",
        "pypandoc==1.11",
        "pypandoc_binary==1.11",
        "PyYAML==6.0",
        "setuptools==58.1.0",
        "spacy==3.5.1",
        "tiktoken==0.3.2"
    ],
    extras_require={
        "dev": [
            # Nothing yet
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Text Processing :: Linguistic",
    ],
    entry_points={
        "console_scripts": [
            "gpt-wn-translator = gpt_wn_translator.main:main",
        ],
    },
    python_requires=">=3.10",
)

        

