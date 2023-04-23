# setup.py

from setuptools import setup, find_packages

with open("README.md", "r") as readme_file:
    long_description = readme_file.read()

setup(
    name="gptwntranslator",
    version="2.1.4",
    author="Rodrigo S. Jauregui",
    author_email="combobulativedesigns@gmail.com",
    description="A web novel translator using OpenAI's GPT API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/combobulativedesigns/gptwntranslator",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "asciimatics==1.14.0",
        "beautifulsoup4==4.12.2",
        "Janome==0.4.2",
        "openai==0.27.2",
        "pypandoc==1.11",
        "pypandoc_binary==1.11",
        "PyYAML==6.0",
        "selenium==4.8.3",
        "spacy==3.5.1",
        "tiktoken==0.3.2",
        "webdriver_manager==3.8.5",
        "yattag==1.15.1",
        "en_core_web_sm @ https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.5.0/en_core_web_sm-3.5.0-py3-none-any.whl",
        "de_core_news_sm @ https://github.com/explosion/spacy-models/releases/download/de_core_news_sm-3.5.0/de_core_news_sm-3.5.0-py3-none-any.whl",
        "es_core_news_sm @ https://github.com/explosion/spacy-models/releases/download/es_core_news_sm-3.5.0/es_core_news_sm-3.5.0-py3-none-any.whl",
        "fr_core_news_sm @ https://github.com/explosion/spacy-models/releases/download/fr_core_news_sm-3.5.0/fr_core_news_sm-3.5.0-py3-none-any.whl",
        "it_core_news_sm @ https://github.com/explosion/spacy-models/releases/download/it_core_news_sm-3.5.0/it_core_news_sm-3.5.0-py3-none-any.whl",
        "ja_core_news_sm @ https://github.com/explosion/spacy-models/releases/download/ja_core_news_sm-3.5.0/ja_core_news_sm-3.5.0-py3-none-any.whl",
        "ko_core_news_sm @ https://github.com/explosion/spacy-models/releases/download/ko_core_news_sm-3.5.0/ko_core_news_sm-3.5.0-py3-none-any.whl",
        "nl_core_news_sm @ https://github.com/explosion/spacy-models/releases/download/nl_core_news_sm-3.5.0/nl_core_news_sm-3.5.0-py3-none-any.whl",
        "pt_core_news_sm @ https://github.com/explosion/spacy-models/releases/download/pt_core_news_sm-3.5.0/pt_core_news_sm-3.5.0-py3-none-any.whl",
        "ru_core_news_sm @ https://github.com/explosion/spacy-models/releases/download/ru_core_news_sm-3.5.0/ru_core_news_sm-3.5.0-py3-none-any.whl",
        "zh_core_web_sm @ https://github.com/explosion/spacy-models/releases/download/zh_core_web_sm-3.5.0/zh_core_web_sm-3.5.0-py3-none-any.whl"
    ],
    extras_require={
        "dev": [
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
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

        

