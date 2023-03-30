# GPT-WN-Translator

GPT-WN-Translator is a web novel translation tool that utilizes OpenAI's GPT models to provide okay-ish/medium-quality translations of Japanese web novels to English. The tool uses web scraping to extract the original text, translates it with the help of AI models, and then generates an epub file for easy reading.

## Capabilities

- Scraping Japanese web novels from Syosetu.
- Translating Japanese text to English using OpenAI's advanced AI models.
- Generating epub files for the translated content.
- Customizable translation by specifying chapters or sub-chapters.
- Skipping specific steps (scraping, translating, or generating epub) as needed.

### Aclaration on Crawling

Syosetu's robots.txt doesn't specify anything about random user agents. When there are no rules specified for a user agent, it implies that any other user agent (web crawlers, search engines, or bots) is allowed to crawl the entire website without any restrictions or crawl delays. I'll still ask you not to multibox this thing and scrape the entire site, pretty please.

### Cost

This tool is free by itself, but it does depend on OpenAI's paid API. I suggest performing your own tests with a small sub-chapter count and setting usage limits on your OpenAI account.

## Installation

Clone the repository and install the package using the following commands:

```bash
git clone https://github.com/your_username/GPT-WN-Translator.git
cd GPT-WN-Translator
pip install .
```

## Configuration

Before using GPT-WN-Translator, ensure you have set up the configuration file (config.yaml) in a "config" subfolder of your working folder. You can find an example configuration file named "config.example.yaml" within the config folder of the cloned repository. In the configuration file, provide your OpenAI API key and enable the AI models you want to use for translation.

## Usage

To use GPT-WN-Translator, you need to provide the working directory path, novel code, and the specific chapters or sub-chapters to translate. You can also choose to skip certain steps like scraping, translating, or generating an epub file.

```bash
gptwntranslator <directory> <novel_code> [-v] [--skip-scraping] [--skip-translating] [--skip-epub] [-c <chapters>]
```

### Arguments:

- `<directory>`: The working directory path.
- `<novel_code>`: The novel code.
- `-c` or `--chapters`: The chapters to translate.
- `-v` or `--verbose`: (Optional) Enable verbose mode.
- `-ss` or `--skip-scraping`: (Optional) Skip scraping the novel.
- `-st` or `--skip-translating`: (Optional) Skip translating the novel.
- `-se` or `--skip-epub`: (Optional) Skip generating the epub.

### Examples:

Scrape, translate, and convert the first chapter of a novel:

```bash
gptwntranslator /home/user/Novels/ 123456 -c 1
```

Translate and convert the first and second chapters of a novel:

```bash
gptwntranslator /home/user/Novels/ 123456 -ss -c 1;2
```

Convert the 5th subchapter of the 3rd chapter of a novel:

```bash
gptwntranslator /home/user/Novels/ 123456 -ss -st -c 3:5
```

Convert the 5th subchapter of the 3rd chapter of a novel in verbose mode:

```bash
gptwntranslator /home/user/Novels/ 123456 -ss -st -c 3:5 -v
```

Scrape, translate, and convert the second to the fifth chapter of a novel:

```bash
gptwntranslator /home/user/Novels/ 123456 -c 2-5
```

Scrape, translate, and convert the second to the fifth subchapter of the third chapter of a novel:

```bash
gptwntranslator /home/user/Novels/ 123456 -c 3:2-5
```

More shenanigans:

```bash
gptwntranslator /home/user/Novels/ 123456 -ss -c 1-3;5-7:8:1-3;9-13 -v
```

### Bad Usage:

You can't specify subchapters for a range of chapters:

```bash
gptwntranslator /home/user/Novels/ 123456 -c 1-3:1-3
```

You can't skip just translating as scraping regenerates the novel object without the translated text, meaning that the epub generation will fail:

```bash
gptwntranslator /home/user/Novels/ 123456 -st -c 1
```

## Current Limitations (or Future Improvements?)

- The tool only works with Japanese web novels from Syosetu.
- The tool doesn't translate:
    - Chapter titles
    - Subchapter titles
    - Novels summaries
    - Author name
    - Novel name
- The tool doesn't generate for the epub file:
    - Table of contents
    - Cover image
    - Author name
    - Novel name

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Or just fork the repository and do whatever you want with it. I'm not your mom.

## License

This project is licensed under the GNU General Public License v3 (GPLv3). See the LICENSE file for more details.

## Acknowledgements

- [OpenAI](https://openai.com/)
For developing the amazing GPT models.
- [Syosetu](https://syosetu.com/)
For providing a great platform for Japanese web novelists.
- [ChatGPT](https://chat.openai.com)
For providing a great amount of help in making this tool. Even this README, wow.



