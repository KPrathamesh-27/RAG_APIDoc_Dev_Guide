import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from concurrent.futures import ThreadPoolExecutor
import time
from urllib.parse import urljoin
import os
import logging
from tqdm import tqdm
import subprocess

# Disable all logging
logging.getLogger('selenium').setLevel(logging.CRITICAL)
os.environ['WDM_LOG_LEVEL'] = '0'

class ParallelCrawler:
    def __init__(self, num_workers=10):
        self.num_workers = num_workers
        self.base_url = "https://www.zoho.com"
        self.output_file = "data.txt"
        
    def init_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--log-level=OFF')
        options.add_argument('--disable-gpu')
        options.add_argument('--silent')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_experimental_option('detach', True)
        
        # Redirect all output to null device
        null_output = open(os.devnull, 'w')
        service = Service(
            service_args=['--verbose', '--log-path=NUL'],
            log_output=null_output,
            stdout=null_output,
            stderr=null_output
        )
        
        driver = webdriver.Chrome(options=options, service=service)
        return driver
        
    def crawl_url(self, url):
        driver = self.init_driver()
        try:
            with open(os.devnull, 'w') as null_output:
                # Redirect stdout/stderr temporarily
                old_stdout, old_stderr = os.dup(1), os.dup(2)
                os.dup2(null_output.fileno(), 1)
                os.dup2(null_output.fileno(), 2)
                
                driver.get(url)
                time.sleep(2)
                
                body = driver.find_element(By.TAG_NAME, 'body')
                
                driver.execute_script("""
                    var header = document.querySelector('header');
                    if (header) header.remove();
                    var footer = document.querySelector('footer');
                    if (footer) footer.remove();
                    var ulElements = document.querySelectorAll('ul');
                    ulElements.forEach(function(ul) {
                        ul.remove();
                    });
                """)
                
                text = body.text
                
                # Restore stdout/stderr
                os.dup2(old_stdout, 1)
                os.dup2(old_stderr, 2)
                
            with open(self.output_file, 'a', encoding='utf-8') as f:
                f.write(f"URL: {url}\n")
                f.write(text)
                f.write('\n\n')
                
        except Exception as e:
            print(f"Error crawling {url}: {str(e)}")
        finally:
            driver.quit()
            
    def process_json(self):
        with open('tree_structure.json', 'r') as f:
            data = json.load(f)
            
        urls = []
        urls.append(data['url'])
        
        for child in data['children']:
            full_url = urljoin(self.base_url, child['url'])
            urls.append(full_url)
            
        return urls
        
    def run(self):
        if os.path.exists(self.output_file):
            os.remove(self.output_file)
            
        urls = self.process_json()
        print(f"Starting to crawl {len(urls)} URLs...")
        
        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            tasks = [executor.submit(self.crawl_url, url) for url in urls]
            for _ in tqdm(tasks, total=len(urls), desc="Crawling Progress"):
                _.result()

if __name__ == "__main__":
    # Redirect ChromeDriver output
    if os.name == 'nt':  # Windows
        DEVNULL = open(os.devnull, 'wb')
        creationflags = subprocess.CREATE_NO_WINDOW
    else:  # Unix
        DEVNULL = open(os.devnull, 'wb')
        creationflags = 0
    
    crawler = ParallelCrawler(num_workers=10)
    crawler.run()