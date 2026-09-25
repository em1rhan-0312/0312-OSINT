import requests
from modules import display as disp

class SocialCrawler:
    def __init__(self):
        # Using a mix of search dorks for simulation since official APIs are restrictive
        self.search_templates = {
            "Twitter/X": "https://www.google.com/search?q=site:twitter.com \"{keyword}\"",
            "LinkedIn": "https://www.google.com/search?q=site:linkedin.com/in/ \"{keyword}\"",
            "Reddit": "https://www.google.com/search?q=site:reddit.com \"{keyword}\"",
            "GitHub": "https://www.google.com/search?q=site:github.com \"{keyword}\""
        }

    def crawl(self, keyword):
        disp.pinfo(f"Crawling social media for keyword: {keyword}...\n")
        disp.pout("Note: This provides search links to avoid API rate limits.\n", disp.YELLOW)
        
        disp.psep()
        for platform, url in self.search_templates.items():
            search_url = url.format(keyword=keyword)
            disp.pout(f" {platform}: ", disp.CYAN)
            disp.pout(f"{search_url}\n", disp.WHITE)
        disp.psep()

def run_social_crawler():
    disp.pheader("SOCIAL MEDIA KEYWORD CRAWLER")
    keyword = disp.pin("Enter keyword to search: ")
    if keyword:
        crawler = SocialCrawler()
        crawler.crawl(keyword)
