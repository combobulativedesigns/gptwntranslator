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
    - [Optional Arguments](#optional-arguments)
    - [Examples](#examples)
- [Current Limitations](#current-limitations)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## Capabilities
---------------

- Scraping Japanese web novels from Syosetu.
- Translating Japanese text using OpenAI's advanced AI models.
- Selection of destination language, if GPT understands it, it can translate to it. With various levels of quality.
- Generating epub files for the translated content.
- Customizable translation by specifying chapters or sub-chapters.
- Selection of AI models to use for translation.
- Optimization of API calls to OpenAI's API.
- Mix and match of AI models for the various steps of the translation process.
- Parallelization of the translation process for faster translations.

### **Aclaration on Crawling**

Syosetu's robots.txt doesn't specify anything about random user agents. When there are no rules specified for random user agents, it implies that any user agent not specifically mentioned (web crawlers, search engines, or bots) is allowed to crawl the entire website without any restrictions or crawl delays. I'll still ask you not to multibox this thing and scrape the entire site, pretty please.

### **Cost**

This tool is free by itself, but it does depend on OpenAI's paid API. I suggest performing your own tests with a small sub-chapter count and setting usage limits on your OpenAI account.

### **Translation Quality**

This tool by no means provides a perfect translation. And does not offer any guarantees on its quality.

All translation is done by OpenAI's GPT models. The quality of the translation depends on the model used, on the model's ability to understand the language, and a bit of luck. As of now, the tool supports the following models: GPT-3.5, GPT-4 8k, GPT-4 32k. The jump in quality from 3.5 to 4 is noticeable, but it's 15 times as expensive as 3.5.

Translation quality itself can also vary if retrying the translation even with the same models. The same input will not always produce the same output. The tool tries to use several techniques to mitigate this, but it's not perfect.

The tool will also be able to use any other model that OpenAI releases in the future, assuming it uses the same API endpoints. This includes the upcoming GPT-5 model, which should be able to produce much better translations.

## Installation
---------------

Clone the repository and install the package using the following commands:

```bash
git clone https://github.com/combobulativedesigns/gptwntranslator.git
cd gptwntranslator
pip install .
```

## Configuration
----------------

Before using gptwntranslator, ensure you have set up the configuration file (config.yaml) in a "config" subfolder of your working folder. You can find an example configuration file named "config.example.yaml" within the config folder of the cloned repository. In the configuration file, provide your OpenAI API key and enable the AI models you want to use for translation. You can also set up the destination language for translations. The default language is English. Other posible languages are specified in the example configuration file.

## Usage
--------

### **Execution**

Depending on how the tool is being used, and if it was installed or not, the tool can be run in different ways.

1. Run the tool as a module:

    ```bash
    python -m gptwntranslator
    ```

2. Run the tool as a script:

    ```bash
    python src/gptwntranslator/__main__.py
    ```

3. Run the tool as a command:

    ```bash
    gptwntranslator
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
    gptwntranslator c ACTION NOVEL_IDENTIFIER [CHAPTERS]
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

All actions require a novel identifier. This is given by the url of the novel. For example, given the novel with url https://ncode.syosetu.com/n7133es/, the novel identifier is the last part of the url. In this case, n7133es.

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

### **Optional Arguments**

Both modes support the following optional arguments:

- Specify the path to a custom configuration file (default: ./config/config.yaml)
    
    `-cf`, `--config-file PATH`
    
- Specify the path to a custom persistent file for tracking progress (default: ./persistent_data.json)

    `-pf`, `--persistent-file PATH`     

- Specify the output directory for generated files (default: ./output)

    `-od`, `--output-directory PATH`

### **Examples**

Given the novel with the following url: https://ncode.syosetu.com/n7133es/

1. Scrape novel metadata:

    ```bash
    gptwntranslator c sm n7133es
    ```

2. Enable verbose output using the -v or --verbose flag:

    ```bash
    gptwntranslator c -v sm n7133es
    ```

3. Scrape novel chapters:

    ```bash
    gptwntranslator c sc n7133es 1-3
    ```

4. Translate novel metadata:

    ```bash
    gptwntranslator c tm n7133es
    ```

5. Translate novel chapters:

    ```bash
    gptwntranslator c tc n7133es 1:1-5
    ```

6. Export novel chapters:

    ```bash
    gptwntranslator c ec n7133es 1:1-5
    ```
    
## Current Limitations
----------------------

- The tool only works with Japanese web novels from Syosetu.
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
- [ChatGPT](https://chat.openai.com)
For providing a great amount of help in making this tool. Even this README, wow.



