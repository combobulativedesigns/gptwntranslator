from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import codecs
import re

options = Options()
options.add_argument("--window-size=1920,1200")
options.add_argument('--headless')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Navigate to the initial URL
# age_confirm_url = 'https://nl.syosetu.com/redirect/ageauth/'  # Replace with the initial URL
initial_url = 'https://novel18.syosetu.com/n5590ft/'  # Replace with the target URL
driver.get(initial_url)

# Set a maximum time to wait (in seconds) for conditions
timeout = 10

# Define the selector for the age confirmation button
age_confirm_button_selector = 'a#yes18'  # Replace with the appropriate CSS selector for the button

# Wait for the page to load
WebDriverWait(driver, timeout).until(
    EC.presence_of_all_elements_located((By.TAG_NAME, 'html'))
)

# Check if the age confirmation button is present
try:
    age_confirm_button = WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, age_confirm_button_selector))
    )
    # Click the age confirmation button if present
    age_confirm_button.click()
    # Wait for the URL to change after clicking the button
    WebDriverWait(driver, timeout).until(
        EC.url_changes(driver.current_url)
    )
except:
    # If the age confirmation button is not present, continue with the current page
    pass

# Get the page source
page_source = driver.page_source

# Create a BeautifulSoup object
soup = BeautifulSoup(page_source, 'html.parser')

# Do whatever you want with the soup

# Close the driver when done
driver.quit()

print(page_source)