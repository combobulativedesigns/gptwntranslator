from gptwntranslator.helpers.config_helper import Config
from gptwntranslator.helpers.ui_helper import UIMenuItem, UIMenuItemType
from gptwntranslator.storage.json_storage import JsonStorage
from gptwntranslator.ui.page_base import PageBase
from gptwntranslator.ui.page_novel_export_targets import PageNovelExportTargets
from gptwntranslator.ui.page_novel_index_update import PageNovelIndexUpdate
from gptwntranslator.ui.page_novel_management import PageNovelManagement
from gptwntranslator.ui.page_novel_scraping_targets import PageNovelScrapingTargets
from gptwntranslator.ui.page_novel_translate_metadata import PageNovelTranslateMetadata
from gptwntranslator.ui.page_novel_translation_targets import PageNovelTranslationTargets
from gptwntranslator.ui.page_return import PageReturn
from gptwntranslator.ui.page_type_a import PageTypeA


class PageNovelMenu(PageTypeA):
    def __init__(self) -> None:

        menu_item_1 = UIMenuItem(UIMenuItemType.PAGE_NAVIGATION, 0, 0, 1, "Update metadata", None, None, PageNovelIndexUpdate, {}, None)
        menu_item_2 = UIMenuItem(UIMenuItemType.PAGE_NAVIGATION, 1, 0, 2, "Download chapters", None, None, PageNovelScrapingTargets, {}, None)
        menu_item_3 = UIMenuItem(UIMenuItemType.PAGE_NAVIGATION, 2, 0, 3, "Translate metadata", None, None, PageNovelTranslateMetadata, {}, None)
        menu_item_4 = UIMenuItem(UIMenuItemType.PAGE_NAVIGATION, 3, 0, 4, "Translate chapters", None, None, PageNovelTranslationTargets, {}, None)
        menu_item_5 = UIMenuItem(UIMenuItemType.PAGE_NAVIGATION, 4, 0, 5, "Export novel", None, None, PageNovelExportTargets, {}, None)
        menu_item_6 = UIMenuItem(UIMenuItemType.PAGE_NAVIGATION, 6, 0, 6, "Novel management", None, None, PageNovelManagement, {}, None)
        menu_item_7 = UIMenuItem(UIMenuItemType.PAGE_NAVIGATION, 8, 0, 0, "Go back", None, None, PageReturn, {}, None)

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
                (6, 0, 0, "0) Go back", PageReturn, "", False)
            ],
            "menu_items2": [
                menu_item_1,
                menu_item_2,
                menu_item_3,
                menu_item_4,
                menu_item_5,
                menu_item_6,
                menu_item_7
            ]
        }

        super().__init__(menu)

    def pre_render(self, screen, **kwargs) -> None:
        super().pre_render(screen, **kwargs)
        storage = JsonStorage()
        novels = storage.get_data()
        novel = [novel for novel in novels if novel.novel_code == kwargs["novel_url_code"]][0]
        cf = Config()
        self.pre_messages = []
        if cf.data.config.translator.target_language in novel.title_translation:
            self.pre_messages.append(u"Novel: {}".format(novel.title_translation[cf.data.config.translator.target_language]))
        else:
            self.pre_messages.append(u"Novel: {}".format(novel.title))
        if cf.data.config.translator.target_language in novel.author_translation:
            self.pre_messages.append(u"Author: {}".format(novel.author_translation[cf.data.config.translator.target_language]))
        else:
            self.pre_messages.append(u"Author: {}".format(novel.author))
        self.pre_messages.append(u"Language: {}".format(novel.original_language))
        self.pre_messages.append(f"Code: {novel.novel_code}")
        self.pre_messages.append(f"Origin: {novel.novel_origin}")

    def process_actions(self, item: UIMenuItem, content) -> tuple[PageBase, dict]:
        if item.page_target is PageReturn:
            return item.page_target, {**item.page_data, **{"return_page": self.args["return_page"], "return_kwargs": self.args["return_kwargs"]}}
        return item.page_target, {**item.page_data, **{"novel_origin": self.args["novel_origin"], "novel_url_code": self.args["novel_url_code"], "return_page": self.__class__, "return_kwargs": self.args}}