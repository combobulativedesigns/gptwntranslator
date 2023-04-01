import json
import sys
import traceback
import yaml
import argparse
from gptwntranslator.api.openai_api import initialize as initialize_openai_api
from gptwntranslator.encoders.json_encoder import JsonEncoder
from gptwntranslator.helpers.args_helper import parse_chapters
from gptwntranslator.helpers.file_helper import read_file, write_file, write_md_as_epub
from gptwntranslator.helpers.text_helper import make_printable, txt_to_md
from gptwntranslator.hooks.object_hook import generic_object_hook
from gptwntranslator.scrapers.syosetu_scraper import process_novel
from gptwntranslator.translators.jp_en_translator import fix_linebreaks, translate_sub_chapter, initialize as initialize_jp_en_translator

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", help="Working directory path")
    parser.add_argument("novel_code", help="Novel code")
    parser.add_argument("-v", "--verbose", help="Verbose mode", action="store_true")
    parser.add_argument("-ss", "--skip-scraping", help="Skip scraping the novel", action="store_true")
    parser.add_argument("-st", "--skip-translating", help="Skip translating the novel", action="store_true")
    parser.add_argument("-se", "--skip-epub", help="Skip generating the epub", action="store_true")
    parser.add_argument("-c", "--chapters", help="The chapters to translate")
    args = parser.parse_args()

    if args.skip_scraping and args.skip_translating and args.skip_epub:
        print("Nothing to do")
        return
    
    if not args.skip_scraping and args.skip_translating and not args.skip_epub:
        print("Can't create epub without translating the novel after a fresh scraping.")
        return
    
    # Clear console
    print("\033c", end="")

    translation_targets = None
    if args.chapters:
        translation_targets = parse_chapters(args.chapters)

    novel_object_output_path = f"{args.directory}/{args.novel_code}/novel.json"
    novel_md_output_path = f"{args.directory}/{args.novel_code}/novel.md"
    novel_epub_output_path = f"{args.directory}/{args.novel_code}/novel.epub"

    try:
        config = yaml.safe_load(read_file("config/config.yaml", args.verbose))
    except Exception as e:
        print(f"Error: Failed to load config file: {e}")
        return

    try:
        api_key = config['config']['openai']['api_key']
        available_models = list(config['config']['openai']['models'].items())
        available_models = {k: {
            'name': v['name'],
            'cost_per_1k_tokens': v['cost_per_1k_tokens'],
            'max_tokens': v['max_tokens']
        } for k, v in available_models if v['enabled']}
    except Exception as e:
        print(f"Error: Failed to load OpenAI API config: {e}")
        return
    
    initialize_openai_api(api_key, available_models)

    try:
        term_models = config['config']['translator']['api']['terms_list']['models']
        translation_models = config['config']['translator']['api']['translation']['models']
        summary_models = config['config']['translator']['api']['summary']['models']
    except Exception as e:
        print(f"Error: Failed to load translator API config: {e}")
        return
    
    print(available_models)
    input("hold")
    
    initialize_jp_en_translator(available_models, term_models, translation_models, summary_models)

    novel = None

    # ========================
    
    if not args.skip_scraping:
        try:
            novel = process_novel(args.novel_code, translation_targets, args.verbose)
            novel_printable = make_printable(json.dumps(novel, ensure_ascii=False, cls=JsonEncoder), args.verbose)
            write_file(novel_object_output_path, novel_printable, args.verbose)
        except Exception as e:
            print(f"Error: Failed to scrape novel: {e}")
            return
        novel = json.loads(novel_printable, object_hook=generic_object_hook)
    else:
        try:
            novel = json.loads(read_file(novel_object_output_path, args.verbose), object_hook=generic_object_hook)
        except Exception as e:
            print(f"Error: Failed to load novel object: {e}")
            return
        
    # ========================
        
    if not args.skip_translating:
        # Iterate over chapters
        for target_chapter in translation_targets.keys():
            target_sub_chapters = translation_targets[target_chapter]
            target_chapter = int(target_chapter)
            # Check if the chapter exists in the novel object
            if target_chapter not in range(1, len(novel.chapters) + 1):
                print(f"Error: Chapter {target_chapter} not found in novel object")
                return
            
            chapter = novel.chapters[target_chapter - 1]
            # iterate over subchapters
            for target_sub_chapter in target_sub_chapters:
                target_sub_chapter = int(target_sub_chapter)
                if target_sub_chapter not in range(1, len(chapter.sub_chapters) + 1):
                    print(f"Error: SubChapter {target_sub_chapter} not found in novel object")
                    return
                
                try:
                    print(f"Translating chapter {target_chapter}, subchapter {target_sub_chapter}... ", end="") if args.verbose else None
                    sys.stdout.flush()
                    translate_sub_chapter(novel, target_chapter - 1, target_sub_chapter - 1, args.verbose)
                    print("Done") if args.verbose else None
                except Exception as e:
                    traceback.print_exc()
                    print(f"Error: {e}")
                    return

        # Write the novel object to file
        try:
            novel_printable = make_printable(json.dumps(novel, ensure_ascii=False, cls=JsonEncoder), args.verbose)
            write_file(novel_object_output_path, novel_printable, args.verbose)
        except Exception as e:
            print(f"Error: {e}")
            return
        novel = json.loads(novel_printable, object_hook=generic_object_hook)

    # ========================

    if not args.skip_epub:
        sub_chapters_md = []
        # Iterate over chapters
        for target_chapter in translation_targets.keys():
            target_sub_chapters = translation_targets[target_chapter]
            target_chapter = int(target_chapter)
            # Check if the chapter exists in the novel object
            if target_chapter not in range(1, len(novel.chapters) + 1):
                print(f"Error: Chapter {target_chapter} not found in novel object")
                return
            
            if len(target_sub_chapters) > 0:
                chapter = novel.chapters[target_chapter - 1]
                # iterate over subchapters
                for target_sub_chapter in target_sub_chapters:
                    target_sub_chapter = int(target_sub_chapter)
                    if target_sub_chapter not in range(1, len(chapter.sub_chapters) + 1):
                        print(f"Error: SubChapter {target_sub_chapter} not found in novel object")
                        return
                    sub_chapter = chapter.sub_chapters[target_sub_chapter - 1]

                    print(f"Compiling chunks of chapter {target_chapter}, subchapter {target_sub_chapter}... ", end="") if args.verbose else None
                    sys.stdout.flush()
                    sub_chapter_text = sub_chapter.name + "\n\n"
                    sub_chapter_text += fix_linebreaks(sub_chapter.translation, sub_chapter.contents)

                    sub_chapter_md = txt_to_md(sub_chapter_text)
                    sub_chapters_md.append(sub_chapter_md)
                    sub_chapter.translation = sub_chapter_text
                    print("Done") if args.verbose else None
            else:
                # If no subchapters are specified, translate all of them
                chapter = novel.chapters[target_chapter - 1]
                # iterate over subchapters
                for target_sub_chapter in range(1, len(chapter.sub_chapters) + 1):
                    sub_chapter = chapter.sub_chapters[target_sub_chapter - 1]

                    print(f"Compiling chunks of chapter {target_chapter}, subchapter {target_sub_chapter}...", end="") if args.verbose else None
                    sys.stdout.flush() 
                    sub_chapter_text = sub_chapter.name + "\n\n"
                    sub_chapter_text += fix_linebreaks(sub_chapter.translation, sub_chapter.contents)

                    sub_chapter_md = txt_to_md(sub_chapter_text)
                    sub_chapters_md.append(sub_chapter_md)
                    sub_chapter.translation = sub_chapter_text
                    print("Done") if args.verbose else None

        # Write the novel object to file
        try:
            novel_printable = make_printable(json.dumps(novel, ensure_ascii=False, cls=JsonEncoder), args.verbose)
            write_file(novel_object_output_path, novel_printable, args.verbose)
        except Exception as e:
            print(f"Error: {e}")
            return

        try:
            print("Writing epub... ", end="") if args.verbose else None
            sys.stdout.flush() 
            write_md_as_epub(sub_chapters_md, novel_epub_output_path, args.verbose)
            print("Done") if args.verbose else None
        except Exception as e:
            print(f"Error: {e}")
            return
        
        try:
            print("Writing markdown... ", end="") if args.verbose else None
            sys.stdout.flush()
            write_file(novel_md_output_path, '\n\n'.join(sub_chapters_md), args.verbose)
            print("Done") if args.verbose else None
        except Exception as e:
            print(f"Error: {e}")
            return


if __name__ == "__main__":
    main()