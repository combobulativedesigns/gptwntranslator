from gptwntranslator.storage.json_storage import JsonStorage
from gptwntranslator.ui.page_novel_editing_target import PageNovelEditingTarget
from gptwntranslator.ui.page_novel_export_targets import PageNovelExportTargets
from gptwntranslator.ui.page_novel_index_update import PageNovelIndexUpdate
from gptwntranslator.ui.page_novel_scraping_targets import PageNovelScrapingTargets
from gptwntranslator.ui.page_novel_translate_metadata import PageNovelTranslateMetadata
from gptwntranslator.ui.page_novel_translation_targets import PageNovelTranslationTargets
from gptwntranslator.ui.page_return import PageReturn
from gptwntranslator.ui.page_type_a import PageTypeA


class PageNovelMenu(PageTypeA):
    def __init__(self) -> None:
        menu = {
            "message_lines": [
                "Actions menu for the novel:",
            ],
            "menu_items": [
                (0, 0, 1, "1) Update metadata", PageNovelIndexUpdate, "", False), 
                (1, 0, 2, "2) Download chapters", PageNovelScrapingTargets, "", False), 
                (2, 0, 3, "3) Translate metadata", PageNovelTranslateMetadata, "", False), 
                (3, 0, 4, "4) Translate chapters", PageNovelTranslationTargets, "", False), 
                # (4, 0, 5, "5) Edit novel", PageNovelEditingTarget, "", False), 
                (4, 0, 5, "5) Export novel", PageNovelExportTargets, "", False), 
                (6, 0, 0, "0) Go back", PageReturn, "", False)]
        }

        super().__init__(menu)

    def pre_render(self, screen, **kwargs) -> None:
        super().pre_render(screen, **kwargs)
        storage = JsonStorage()
        novels = storage.get_data()
        novel = [novel for novel in novels if novel.novel_code == kwargs["novel_url_code"]][0]
        self.pre_messages = []
        if novel.title_translation:
            self.pre_messages.append(u"Novel: {}".format(novel.title_translation))
        else:
            self.pre_messages.append(u"Novel: {}".format(novel.title))
        if novel.author_translation:
            self.pre_messages.append(u"Author: {}".format(novel.author_translation))
        else:
            self.pre_messages.append(u"Author: {}".format(novel.author))
        self.pre_messages.append(u"Language: {}".format(novel.original_language))
        self.pre_messages.append(f"Code: {novel.novel_code}")

    def process_actions(self, item, content):
        if item[4] is PageReturn:
            return item[4], {"return_page": self.args["return_page"], "return_kwargs": self.args["return_kwargs"]}
        return item[4], {"novel_url_code": self.args["novel_url_code"], "return_page": self.__class__, "return_kwargs": self.args}