from subprocess import CREATE_NO_WINDOW
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from gptwntranslator.helpers.logger_helper import CustomLogger
from gptwntranslator.origins.syosetu_base_origin import SyosetuBaseOrigin


logger = CustomLogger(__name__)

class SyosetuNovel18Origin(SyosetuBaseOrigin):
    @classmethod
    @property
    def code(cls):
        return "syosetu_novel18"
    
    @classmethod
    @property
    def name(cls):
        return "Syosetu Novel18"
    
    def __init__(self) -> None:
        location = "https://novel18.syosetu.com/"
        super().__init__(location)

    def _get_soup(self, url: str) -> BeautifulSoup:
        if not isinstance(url, str):
            raise ValueError(f"URL {url} should be a string")
        if not urlparse(url).scheme:
            raise ValueError(f"URL {url} should have a scheme")
        if not urlparse(url).netloc:
            raise ValueError(f"URL {url} should have a netloc")
        
        options = Options()
        options.add_argument("--window-size=1920,1200")
        options.add_argument('--headless')
        options.add_argument("--silent");

        try:
            svc = Service(ChromeDriverManager().install())
            svc.creation_flags = CREATE_NO_WINDOW
            with webdriver.Chrome(service=svc, options=options) as driver:
                driver.get(url)

                timeout = 15

                age_confirm_button_selector = 'a#yes18'

                WebDriverWait(driver, timeout).until(
                    EC.presence_of_all_elements_located((By.TAG_NAME, 'html'))
                )

                try:
                    age_confirm_button = WebDriverWait(driver, timeout).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, age_confirm_button_selector))
                    )
                    age_confirm_button.click()
                    WebDriverWait(driver, timeout).until(
                        EC.url_changes(driver.current_url)
                    )
                except:
                    pass

                page_source = driver.page_source
        except Exception as e:
            logger.error(f"Error while getting page source from {url}. Error: {e}")
            raise e

        return BeautifulSoup(page_source, 'html.parser')