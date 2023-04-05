"""Module for data helper functions."""

from gptwntranslator.models.novel import Novel
from gptwntranslator.models.sub_chapter import SubChapter


def get_targeted_sub_chapters(novel: Novel, targets: dict[str, list[str]]) -> list[SubChapter]:
    """Get a list of sub chapters from a novel based on a list of targets.

    Parameters
    ----------
    novel : Novel
        The novel to get the sub chapters from.
    targets : dict[str, list[str]]
        A dictionary of chapter numbers and subchapter numbers.

    Returns
    -------
    list[SubChapter]
        A list of sub chapters from the novel.
    """

    # Validate parameters
    if not isinstance(novel, Novel):
        raise TypeError("Novel must be a Novel")
    if not isinstance(targets, dict):
        raise TypeError("Targets must be a dictionary")
    if not all(isinstance(key, str) for key in targets.keys()):
        raise TypeError("Chapter numbers must be strings")
    if not all(key.isdigit() for key in targets.keys()):
        raise TypeError("Chapter numbers must be digits as strings")
    if not all(isinstance(value, list) for value in targets.values()):
        raise TypeError("Sub chapter numbers must be lists")
    if not all(isinstance(item, str) for value in targets.values() for item in value):
        raise TypeError("Sub chapter numbers must be strings")
    if not all(item.isdigit() for value in targets.values() for item in value):
        raise TypeError("Sub chapter numbers must be digits as strings")

    # Initialize the result list
    result = []

    # Iterate over the chapters
    for chapter in novel.chapters:
        # Check if the chapter is targeted
        if chapter.number in targets:
            # Check if the chapter has sub chapters
            if chapter.sub_chapters is not None:
                # Iterate over the sub chapters
                for sub_chapter in chapter.sub_chapters:
                    # Check if the sub chapter is targeted
                    if sub_chapter.number in targets[chapter.number]:
                        # Add the sub chapter to the result list
                        result.append(sub_chapter)
            else:
                # Add all sub chapters to the result list
                result.extend(chapter.sub_chapters)

    return result