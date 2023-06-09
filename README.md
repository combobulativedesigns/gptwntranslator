# gptwntranslator

gptwntranslator is a web novel translation tool that utilizes OpenAI's GPT models to provide okay-ish/medium-quality translations of mainly Japanese web novels. The tool uses web scraping to extract the original text, translates it with the help of AI models, and then generates an epub file for easy reading. 

## Table of Contents
---------------------

- [Capabilities](#capabilities)
    - [Aclaration on Crawling](#aclaration-on-crawling)
    - [Cost](#cost)
    - [Translation Quality](#translation-quality)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
    - [Execution](#execution)
    - [Modes](#modes)
    - [Interactive Mode](#interactive-mode)
    - [Command Mode](#command-mode)
    - [Novel Origins](#novel-origins)
    - [Optional Arguments](#optional-arguments)
    - [Extra Actions](#extra-actions)
    - [Examples](#examples)
- [Current Limitations](#current-limitations)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## Capabilities
---------------

- Scraping web novels from multiple sites.
- Translating text using OpenAI's advanced AI models.
- Translation from and to multiple languages.
- Generating epub files for the translated content.
- Customizable translation by specifying chapters or sub-chapters.
- Selection of AI models to use for translation.
- Optimization of API calls to OpenAI's API.
- Mix and match of AI models for the various steps of the translation process.
- Parallelization of the translation process for faster translations.
- Caching of scraped web novels to avoid unnecessary scraping.
- Caching of translated text to avoid unnecessary API calls.
- Exporting / importing of cached data for easy sharing and editing.

### **Aclaration on Crawling**

All urls the tool scrapes are not covered by the sites' robots.txt files, which implies that the tool is not violating any terms of service. However, I'll still like to ask you not to scrape the entire sites at once. Stay within sane limits and don't abuse the tool.

### **Cost**

This tool is free by itself, but it does depend on OpenAI's paid API. I suggest performing your own tests with a small sub-chapter count and setting usage limits on your OpenAI account.

### **Translation Quality**

This tool by no means provides a perfect translation. And does not offer any guarantees on its quality.

All translation is done by OpenAI's GPT models. The quality of the translation depends on the model used, on the model's ability to understand the language, and a bit of luck. As of now, the tool supports the following models: GPT-3.5, GPT-4 8k, GPT-4 32k. The jump in quality from 3.5 to 4 is noticeable, but it's 15 times as expensive as 3.5.

Translation quality itself can also vary if retrying the translation even with the same models. The same input will not always produce the same output. The tool tries to use several techniques to mitigate this, but it's not perfect.

The tool will also be able to use any other model that OpenAI releases in the future, assuming it uses the same API endpoints. This includes the upcoming GPT-5 model, which should be able to produce much better translations.

## Installation
---------------

1. Go to the sidebar, find the `Releases` section and click on the latest release.
2. On the release page, download the source code found on the Assets section. If you don't know which file to download, select the Zip one.
3. Once downloaded, extract the zip to a location of your preference.
4. Open a terminal inside the extraction folder.
5. (Optional) Create a virtual environment
    1. Enter `python -m venv .venv` in the terminal for creating the environment inside a .venv folder.
    2. Activate the environment by running `.\.venv\Scripts\activate` in the terminal.
6. Install the program running `python -m pip install .`

## Configuration
----------------

Before using gptwntranslator, ensure you have set up the configuration file (config.yaml) in a "config" subfolder of your working folder. You can find an example configuration file named "config.example.yaml" within the config folder of the cloned repository. In the configuration file, provide your OpenAI API key and enable the AI models you want to use for translation. You can also set up the destination language for translations. The default language is English. Other posible languages are specified in the example configuration file.

## Usage
--------

### **Execution**

1. With a virtual environment

If you created a virtual environment while installing, make sure it is activated before running the app by running `.\.venv\Scripts\activate` inside the program folder. Then you can run the program using: 

```bash
gptwntranslator
```

You can return to the normal python environment once done with the program by running `deactivate` in the terminal where you activated the environment. You can also just close the terminal since activating an environment is only relevant for the terminal where the activation command is run.

2. As a script

You can run the program as a script entering the following command inside a terminal located in the program folder:

```bash
python src/gptwntranslator/__main__.py
```

### **Modes**

The tool supports two main modes: interactive and command. You can also access this in-depth help by using the 'help' command.

1. Help

    Run the tool in help mode by using the 'help' or 'h' command:

    ```bash
    gptwntranslator h
    ```

1. Interactive Mode:

    Run the tool in interactive mode by using the 'interactive' or 'i' command:

    ```bash    
    gptwntranslator i
    ```

2. Command Mode:

    Run the tool in command mode by using the 'command' or 'c' command:

    ```bash
    gptwntranslator c ACTION NOVEL_ORIGIN NOVEL_IDENTIFIER [CHAPTERS]
    ```

### **Interactive Mode**

Interactive mode will guide you through the process of scraping, translating, and exporting a novel. It will ask you for the novel identifier, load it from the local cache if it exists, scrape it if it doesn't, and then present you with a menu of options. This options match the actions available in command mode, and follow the same rules.

### **Command Mode**

Command mode requires an action, a novel identifier, and optionally chapters depending on the action. Available actions:

- scrape-metadata (sm): Scrape novel metadata
- scrape-chapters (sc): Scrape novel chapters
- translate-metadata (tm): Translate novel metadata
- translate-chapters (tc): Translate novel chapters
- export-chapters (ec): Export novel chapters

All actions require a novel origin and identifier. The latter is given by the url of the novel. For example, given the novel with url https://ncode.syosetu.com/n7133es/, the novel identifier is the last part of the url. In this case, n7133es.

Actions that require chapters to be specified will also require a list of chapters to be processed. This actions are 'sc', 'tc', and 'ec'. The chapters can be specified in the following formats:

- Chapter numbers are represented by one or more digits (e.g., \"3\" or \"12\").
- Sub-chapter numbers are also represented by one or more digits (e.g., \"4\" or \"23\").
- Chapter ranges are represented by two chapter numbers separated by a hyphen (e.g., \"2-5\").
- Sub-chapter ranges are represented by two sub-chapter numbers separated by a hyphen (e.g., \"6-9\").
- A chapter can be followed by a colon and a list of sub-chapters or sub-chapter ranges (e.g., \"3:2,5,7-9\").
- Individual chapters or chapter ranges can be separated by semicolons (e.g., \"3:2,5;5-7;8:1-3,5\").

Here's an example input that would match this pattern:

    1:1,3,5-7;2-4;5:1-3,6;6-8

This translates to:

- Chapter 1, sub-chapters 1, 3, 5, 6, 7
- Chapters 2, 3, 4. All sub-chapters.
- Chapter 5, sub-chapters 1, 2, 3, 6
- Chapters 6, 7, 8. All sub-chapters.

All actions but 'sm' require previously scraped metadata. If the metadata is not found, the tool will terminate.

Translate actions require a previous scrape action. If the chapters are not found, the tool will terminate.

Export actions require a previous translate action. If the chapters are not found, the tool will terminate. 

### **Novel Origins**

The tool supports the following novel origins:

- syosetu_ncode: Syosetu novel with ncode url (e.g., https://ncode.syosetu.com/n7133et/)
- syosetu_novel18: Syosetu novel with novel18 url (e.g., https://novel18.syosetu.com/n5590ft/)
- kakuyomu: Kakuyomu novel (e.g., https://kakuyomu.jp/works/16816927861321881557)
- jjwxc: JJWXC novel (e.g., https://www.jjwxc.net/onebook.php?novelid=3297507)

### **Optional Arguments**

Both modes support the following optional arguments:

- Specify the path to a custom configuration file (default: ./config/config.yaml)
    
    `-cf`, `--config-file PATH`
    
- Specify the path to a custom persistent file for tracking progress (default: ./persistent_data.json)

    `-pf`, `--persistent-file PATH`     

- Specify the output directory for generated files (default: ./output)

    `-od`, `--output-directory PATH`

- Specify the input directory for importing files (default: ./input)

    `-id`, `--input-directory PATH`

### **Extra Actions**

When using the tool in interactive mode, you can also use navigate the menu to perform the following actions:

- Import / Esport a novel: Import a novel from a file or export a novel to a file.
- Import / Export a term sheet: Import a term sheet from a file or export a term sheet to a file.
- Purging a novel's cache:
    - Purge novel summary: Purge the novel summary from the cache.
    - Purge novel term sheet: Purge the novel term sheet from the cache.
    - Purge novel completely: Purge the novel from the cache.

### **Examples**

Given the novel with the following url: https://ncode.syosetu.com/n7133es/

1. Scrape novel metadata:

    ```bash
    gptwntranslator c sm syosetu_ncode n7133es
    ```

2. Enable verbose output using the -v or --verbose flag:

    ```bash
    gptwntranslator c -v sm syosetu_ncode n7133es
    ```

3. Scrape novel chapters:

    ```bash
    gptwntranslator c sc syosetu_ncode n7133es 1-3
    ```

4. Translate novel metadata:

    ```bash
    gptwntranslator c tm syosetu_ncode n7133es
    ```

5. Translate novel chapters:

    ```bash
    gptwntranslator c tc syosetu_ncode n7133es 1:1-5
    ```

6. Export novel chapters:

    ```bash
    gptwntranslator c ec syosetu_ncode n7133es 1:1-5
    ```
    
## Current Limitations
----------------------

- ~~The tool only works with Japanese web novels from Syosetu.~~
- ~~The tool doesn't translate:~~
    - ~~Chapter titles~~
    - ~~Subchapter titles~~
    - ~~Novels summaries~~
    - ~~Author name~~
    - ~~Novel name~~
- ~~The tool doesn't generate for the epub file:~~
    - ~~Table of contents~~
    - ~~Cover image~~
    - ~~Author name~~
    - ~~Novel name~~

## Contributing
---------------

We could use testing, so if you want to help out, please do. We also need people to verify the quality of translations for most languages.

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Or just fork the repository and do whatever you want with it. I'm not your mom.

## License
----------

This project is licensed under the GNU General Public License v3 (GPLv3). See the [LICENSE](LICENSE) file for more details.

## Acknowledgements
-------------------

- [OpenAI](https://openai.com/)
For developing the amazing GPT models.
- [Syosetu](https://syosetu.com/)
For providing a great platform for Japanese web novelists.
- [Kakuyomu](https://kakuyomu.jp/)
For providing another great platform for Japanese web novelists.
- [jjwxc](https://www.jjwxc.net)
For providing a great platform for Chinese web novelists.
- [ChatGPT](https://chat.openai.com)
For providing a great amount of help in making this tool. Even this README, wow.



