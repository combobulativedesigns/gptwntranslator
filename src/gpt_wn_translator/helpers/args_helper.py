def parse_chapters(input_string):
    chapters = input_string.split(';')
    result = {}

    for chapter in chapters:
        chapter_parts = chapter.split(':')
        
        if '-' in chapter_parts[0]:
            start, end = chapter_parts[0].split('-')
            for i in range(int(start), int(end) + 1):
                result[str(i)] = []
        else:
            chapter_number = chapter_parts[0]
            if len(chapter_parts) > 1:
                sub_chapters = chapter_parts[1].split(',')
                expanded_sub_chapters = []
                
                for sub_chapter in sub_chapters:
                    if '-' in sub_chapter:
                        start, end = sub_chapter.split('-')
                        expanded_sub_chapters.extend([f"{i}" for i in range(int(start), int(end) + 1)])
                    else:
                        expanded_sub_chapters.append(f"{sub_chapter}")

                result[chapter_number] = expanded_sub_chapters
            else:
                result[chapter_number] = []
    
    return result