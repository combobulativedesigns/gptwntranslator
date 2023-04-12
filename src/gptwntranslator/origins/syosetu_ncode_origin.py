from urllib.request import urlopen
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from gptwntranslator.origins.syosetu_base_origin import SyosetuBaseOrigin


class SyosetuNCodeOrigin(SyosetuBaseOrigin):
    @classmethod
    @property
    def code(cls):
        return "syosetu_ncode"
    
    @classmethod
    @property
    def name(cls):
        return "Syosetu NCode"
    
    def __init__(self) -> None:
        location = "https://ncode.syosetu.com/"
        super().__init__(location)

    # def _get_soup(self, url: str) -> BeautifulSoup:
    #     if not isinstance(url, str):
    #         raise ValueError(f"URL {url} should be a string")
    #     if not urlparse(url).scheme:
    #         raise ValueError(f"URL {url} should have a scheme")
    #     if not urlparse(url).netloc:
    #         raise ValueError(f"URL {url} should have a netloc")
        
    #     html = urlopen(url)
    #     soup = BeautifulSoup(html, 'html.parser')
    #     return soup