from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
import time

# Function to fetch and parse HTML from a URL using Selenium
def fetch_html_with_selenium(driver, url):
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        return BeautifulSoup(driver.page_source, 'html.parser')
    except Exception as e:
        print(f"Error fetching URL {url}: {e}")
        return None

# Function to recursively build the tree structure
def build_tree(driver, url, depth=0, max_depth=2):
    if depth > max_depth:
        return None  # Stop recursion beyond max depth

    print(f"Processing: {url} at depth {depth}")
    time.sleep(3)
    soup = fetch_html_with_selenium(driver, url)
    if soup is None:
        return None

    # Initialize the node with the URL as the root
    tree = {'url': url, 'children': []}
    time.sleep(3)
    # Find all top-level <ul> elements
    ul_elements = soup.find_all('ul', recursive=True)
    for ul in ul_elements:
        for li in ul.find_all('li', recursive=False):  # Direct children only
            node = {}
            link = li.find('a')  # Find link within <li>
            if link:
                node['title'] = link.text.strip()
                node['url'] = link.get('href', None)

                if node['url']:
                    tree['children'].append(node)
    return tree

# Main execution
if __name__ == "__main__":

    root_url = "https://www.zoho.com/books/api/v3/"  # Replace with the desired starting URL
    driver = webdriver.Chrome()
    try:
        json_structure = build_tree(driver, root_url, max_depth=3)
        with open("tree_structure.json", "w") as f:
            json.dump(json_structure, f, indent=2)
    finally:
        driver.quit() 
