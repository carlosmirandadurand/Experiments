import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from urllib.parse import urlparse
import os
import re
from datetime import datetime
import logging

class WebCrawlerSpider(CrawlSpider):
    name = "web_crawler"
    allowed_domains = []
    start_urls = []
    rules = (
        Rule(LinkExtractor(deny=(), allow=()), callback='parse_item', follow=True),
    )
    logger = None  # Define the logger attribute as a class variable

    def __init__(self, url_list, max_depth=5, *args, **kwargs):
        super(WebCrawlerSpider, self).__init__(*args, **kwargs)
        self.start_urls = [url.strip() for url in url_list]
        self.allowed_domains = [urlparse(url).netloc for url in self.start_urls]
        self.max_depth   = int(max_depth) # TBC depth_limit
        self.job_start_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.setup_logger()  # Call the setup_logger method to initialize the logger

    def setup_logger(self):
        log_dir = f'downloads/_all_/{self.job_start_timestamp}/'
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, 'crawl.log')
        logging.basicConfig(
            filename=log_file,
            format='%(asctime)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )
        self.logger = logging.getLogger(__name__)  # Assign the logger instance to the class attribute

    def parse_item(self, response):
        print(f"Custom Spider parse_item: url: {response.url}")
        clean_url = re.sub(r'[^\w\-_\. ]', '_', urlparse(response.url).netloc)
        output_dir = f'downloads/{clean_url}/{self.job_start_timestamp}/content/'
        os.makedirs(output_dir, exist_ok=True)

        #file_name = f"{response.url.split('/')[-1] or 'index'}.html"
        file_name = re.sub(r'[^\w\-_\. ]', '_', response.url)
        file_path = os.path.join(output_dir, file_name)
        self.logger.info(f"Saving page: {response.url}")

        try:
            with open(file_path, 'wb') as f:
                f.write(response.body)
            self.logger.info(f"Successfully saved: {file_path}")
        except Exception as e:
            self.logger.error(f"Error saving {response.url}: {str(e)}")

if __name__ == "__main__":
    url_list = ["http://example.com", 
                "https://proactiveingredient.com",    
                ] 
    max_depth  = 5  # To be implemented: Number of levels down from the home page
    rate_limit = 5  # To be implemented: Max frequency (requests per second) 

    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'LOG_LEVEL': 'DEBUG',     # INFO, DEBUG
        'ROBOTSTXT_OBEY': False,  # True, False
    })

    process.crawl(WebCrawlerSpider, url_list=url_list, max_depth=max_depth)
    process.start()