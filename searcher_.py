import os
import re
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from urllib.parse import urlparse
from bs4 import BeautifulSoup

import string

import sys
for a in ['']:
    sys.path.append(a)
#

class Searcher:

    def __init__(self):
        self.cp = os.getcwd()  # Current path
        self.firefox_instance = None
        self.search_engines = ["https://www.google.com/search?q="]
        self.current_search_engine = 0
        self.words = []
        self.current_word = None
        self.dementor = ','  # Default delimiter for parsing words
        self.count_urls = 0
        self.i=0

    def set_path(self, path: str):
        """Sets the current path."""
        self.cp = path

    def get_path(self):
        """Returns the current path."""
        return self.cp

    def get_firefox(self):
        """Initializes and returns the Firefox instance (singleton)."""
        if not self.firefox_instance:
            options = Options()
            options.headless = True#False
            options.log.level = 0
            # options.service_log_path = "C:\\Users\\[username]\\AppData\\Local\\Temp\\geckodriver.log"
            options.binary_location = r".\firefox.exe"
            self.firefox_instance = webdriver.Firefox(options=options)
        return self.firefox_instance

    def read(self):
        """Searches the current word using the current search engine and returns the result and title."""
        self.i += 1
        if self.i > 9:
            self.i=0
            self.firefox_instance.quit()
            self.firefox_instance = None
        firefox = self.get_firefox()
        firefox.get(self.current_search)
        try:
            res = firefox.page_source
        except:
            res = 'nic'

        title = firefox.execute_script('return document.title')
        return res, title

    def save(self, html, title):
        """Saves the HTML content to a file using the DTTFacade."""
        title = self.sanitize_filename(title)
        with open(os.path.join(self.get_path(), title + '.html'), 'w') as f:
            f.write(html)

    def set_search_engines(self, engines: list):
        """Sets the search engines."""
        self.search_engines = engines

    def get_search_engines(self):
        """Returns the search engines."""
        return self.search_engines

    def next_search_engine(self):
        """Iterates to the next search engine."""
        self.current_search_engine = (self.current_search_engine + 1) % len(self.search_engines)

    def get_current_search_engine(self):
        """Returns the current search engine."""
        return self.search_engines[self.current_search_engine]

    def set_words(self, words: str):
        """Parses the input string to an array of words and URLs."""
        self.words = self.parse(words)
        self.count_urls = sum(1 for word in self.words if self.is_url(word))

    def parse(self, string: str):
        """Parses the input string to an array of words and URLs."""
        words = re.split(self.dementor, string)
        return self.urls_put_first(words)

    def urls_put_first(self, words: list):
        """Sorts the words so that URLs come first."""
        return sorted(words, key=lambda word: not self.is_url(word))

    def is_url(self, arg: str):
        """Returns True if the argument is a URL."""
        # try:
        #     result = urlparse(arg)
        #     return all([result.scheme, result.netloc])
        # except ValueError:
        #     return False
        return re.match(r'https?://(www\.)?\S+', arg) is not None

    def add_word(self, word: str):
        """Adds a word to the list of words to search."""
        self.words.append(word)

    def next_word(self):
        """Returns and removes the next word to search."""
        self.current_word = self.words.pop(0)
        return self.current_word


    def sanitize_filename(self, filename: str, max_length: int = 255) -> str:
        """
        Sanitizes a string to make it a valid filename in Python.

        :param filename: The input string to sanitize.
        :param max_length: The maximum length for the filename (default: 255).
        :return: The sanitized filename.
        """
        # Remove invalid characters
        valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        filename = ''.join(c for c in filename if c in valid_chars)

        # Replace spaces with underscores
        filename = filename.replace(' ', '_')

        # Truncate the filename to the maximum length
        filename = filename[:max_length]

        # Ensure the filename does not start or end with a dot or an underscore
        filename = re.sub(r'^[._]+|[._]+$', '', filename)

        return filename


    def search_all_words(self):
        """Searches all words and URLs."""
        while self.words:
            if self.is_url(self.next_word()):
                self.search_url()
            else:
                self.search_word()

    def search_url(self):
        """Searches a URL and saves the result."""
        self.set_current_search(self.current_word)
        html, title = self.read()
        self.save(html, title)

    def search_word(self):
        """Searches a word using all search engines and adds URLs to the list of words to search."""
        for engine in self.get_search_engines():
            self.set_current_search(engine + self.current_word)
            html, _ = self.read()
            urls = self.pick_urls(html)
            for url in urls:
                self.add_word(url)

    def pick_urls(self, html: str):
        """Extracts URLs from the HTML content using XPath."""

        soup = BeautifulSoup(html, 'html.parser')
        return [a['href'] for a in soup.find_all('a', href=True) if self.is_url(a['href'])]
        # urls = firefox.find_elements_by_xpath("//a[@href]")
        # return [url.get_attribute('href') for url in urls]

    def set_current_search(self, search: str):
        """Sets the current search term."""
        self.current_search = search

    def set_dementor(self, dementor: str):
        """Sets the delimiter for parsing words."""
        self.dementor = dementor
