import re
import requests
from urllib.parse import urlparse
from typing import List, Set, Tuple, Any, Dict
from core.requester import Requester
from core.config import ScanContext
from core.log import setup_logger

logger = setup_logger()

class PhotonCrawler:
    def __init__(self, context: ScanContext):
        self.context = context
        self.requester = Requester(context)
        self.visited: Set[str] = set()
        self.forms: List[Dict[str, Any]] = []
        self.urls: Set[str] = set()

    def crawl(self, seed_url: str, depth: int = 2) -> Tuple[List[Dict[str, Any]], Set[str]]:
        """
        Crawls the target URL recursively up to a specified depth.
        Extracts forms and internal URLs.
        """
        logger.run(f"Photon Crawler started for {seed_url} (Depth: {depth})")
        
        queue = [(seed_url, 1)]
        parsed_seed = urlparse(seed_url)
        domain = parsed_seed.netloc
        
        while queue:
            url, current_depth = queue.pop(0)
            if url in self.visited or current_depth > depth:
                continue
                
            self.visited.add(url)
            logger.debug(f"Crawling: {url}")
            
            try:
                response = self.requester.request(url)
                response_text = response.text
                
                # Extract Forms (Simplified)
                self._extract_forms(url, response_text)
                
                # Extract URLs
                new_urls = self._extract_urls(url, response_text, domain)
                for new_url in new_urls:
                    if new_url not in self.visited:
                        queue.append((new_url, current_depth + 1))
                        self.urls.add(new_url)
                        
            except Exception as e:
                logger.error(f"Failed to crawl {url}: {e}")
                
        logger.good(f"Crawl finished. Found {len(self.forms)} forms and {len(self.urls)} internal URLs.")
        return self.forms, self.urls

    def _extract_forms(self, url: str, html: str):
        """Extracts HTML forms and their input fields."""
        # Find forms
        form_pattern = re.compile(r'<form[^>]*?>(.*?)</form>', re.IGNORECASE | re.DOTALL)
        for form_match in form_pattern.finditer(html):
            form_content = form_match.group(1)
            
            # Extract action
            action_match = re.search(r'action=["\']([^"\']*?)["\']', html[form_match.start():form_match.end()], re.IGNORECASE)
            action = action_match.group(1) if action_match else url
            
            # Extract method
            method_match = re.search(r'method=["\'](POST|GET)["\']', html[form_match.start():form_match.end()], re.IGNORECASE)
            method = method_match.group(1).upper() if method_match else 'GET'
            
            # Extract input fields
            inputs = []
            input_pattern = re.compile(r'<(?:input|textarea|select)[^>]*?name=["\']([^"\']*?)["\']', re.IGNORECASE)
            for input_match in input_pattern.finditer(form_content):
                inputs.append(input_match.group(1))
            
            if inputs:
                self.forms.append({
                    'action': action,
                    'origin': url,
                    'method': method,
                    'inputs': inputs
                })

    def _extract_urls(self, url: str, html: str, domain: str) -> Set[str]:
        """Extracts internal URLs from a page."""
        internal_urls = set()
        url_pattern = re.compile(r'href=["\'](https?://[^"\']*?|/[^"\']*?)["\']', re.IGNORECASE)
        
        for match in url_pattern.finditer(html):
            extracted = match.group(1)
            if extracted.startswith('/'):
                # Relative to domain root
                parsed = urlparse(url)
                extracted = f"{parsed.scheme}://{parsed.netloc}{extracted}"
            
            # Check if internal
            if domain in extracted:
                internal_urls.add(extracted)
        return internal_urls

# Legacy wrapper for compatibility
def photon(seed_url, headers, depth, threads, delay, timeout, skipDOM):
    from core.config import XSSConfig
    config = XSSConfig(delay=delay, timeout=timeout, threadCount=threads)
    context = ScanContext(config=config, headers=headers)
    crawler = PhotonCrawler(context)
    return crawler.crawl(seed_url, depth)
