from gptwntranslator.helpers.config_helper import Config
from gptwntranslator.helpers.ui_helper import UIMenuItem, UIMenuItemType
from gptwntranslator.storage.json_storage import JsonStorage
from gptwntranslator.ui.page_base import PageBase
from gptwntranslator.ui.page_novel_mgm_export_json import PageNovelMgmExportJson
from gptwntranslator.ui.page_novel_mgm_export_sheet import PageNovelMgmExportSheet
from gptwntranslator.ui.page_novel_mgm_import_json import PageNovelMgmImportJson
from gptwntranslator.ui.page_novel_mgm_import_sheet import PageNovelMgmImportSheet
from gptwntranslator.ui.page_novel_mgm_purge_novel import PageNovelMgmPurgeNovel
from gptwntranslator.ui.page_novel_mgm_purge_sheet import PageNovelPurgeSheet
from gptwntranslator.ui.page_novel_mgm_purge_summaries import PageNovelMgmPurgeSummaries
from gptwntranslator.ui.page_return import PageReturn
from gptwntranslator.ui.page_type_a import PageTypeA


class PageNovelManagement(PageTypeA):
    def __init__(self) -> None:

        menu_item_1 = UIMenuItem(UIMenuItemType.PAGE_NAVIGATION, 0, 0, 1, "Export Json", None, None, PageNovelMgmExportJson, {}, None)
        menu_item_2 = UIMenuItem(UIMenuItemType.PAGE_NAVIGATION, 1, 0, 2, "Import Json", None, None, PageNovelMgmImportJson, {}, None)
        menu_item_3 = UIMenuItem(UIMenuItemType.PAGE_NAVIGATION, 3, 0, 3, "Export term sheet", None, None, PageNovelMgmExportSheet, {}, None)
        menu_item_4 = UIMenuItem(UIMenuItemType.PAGE_NAVIGATION, 4, 0, 4, "Import term sheet", None, None, PageNovelMgmImportSheet, {}, None)
        menu_item_5 = UIMenuItem(UIMenuItemType.PAGE_NAVIGATION, 6, 0, 5, "Purge summaries", None, None, PageNovelMgmPurgeSummaries, {}, None)
        # menu_item_6 = UIMenuItem(UIMenuItemType.PAGE_NAVIGATION, 7, 0, 6, "Purge translations", None, None, PageMessage, {"messages": ["Under construction"]}, None)
        menu_item_7 = UIMenuItem(UIMenuItemType.PAGE_NAVIGATION, 7, 0, 6, "Purge term sheet", None, None, PageNovelPurgeSheet, {}, None)
        menu_item_8 = UIMenuItem(UIMenuItemType.PAGE_NAVIGATION, 9, 0, 7, "Purge novel (ALL)", None, None, PageNovelMgmPurgeNovel, {}, None)
        menu_item_9 = UIMenuItem(UIMenuItemType.PAGE_NAVIGATION, 11, 0, 0, "Go back", None, None, PageReturn, {}, None)

        menu ={
            "message_lines": [
                "Here you have the options to manage your novel.",
            ],
            "menu_items2": [
                menu_item_1,
                menu_item_2,
                menu_item_3,
                menu_item_4,
                menu_item_5,
                # menu_item_6,
                menu_item_7,
                menu_item_8,
                menu_item_9,
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
