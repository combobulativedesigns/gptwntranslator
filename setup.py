# setup.py

from setuptools import setup, find_packages

with open("README.md", "r") as readme_file:
    long_description = readme_file.read()

setup(
    name="gptwntranslator",
    version="0.1.0",
    author="Rodrigo S. Jauregui",
    author_email="ro.sjda42@gmail.com",
    description="A web novel translator using gpt-3.5-turbo and gpt-4",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/CombobulativeDesigns/GPTWebNovelTranslator",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    py_modules=["main"],
    install_requires=[
        "beautifulsoup4==4.12.0",
        "Janome==0.4.2",
        "openai==0.27.2",
        "pypandoc==1.11",
        "pypandoc_binary==1.11",
        "PyYAML==6.0",
        "spacy==3.5.1",
        "tiktoken==0.3.2",
        "ja_core_news_sm @ https://github.com/explosion/spacy-models/releases/download/ja_core_news_sm-3.5.0/ja_core_news_sm-3.5.0-py3-none-any.whl",
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
            "gptwntranslator = gptwntranslator.__main__:main",
        ],
    },
    python_requires=">=3.10",
)

        

