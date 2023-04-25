import copy
from datetime import datetime
from typing import Optional, List

from bs4 import Tag

from aalto_news_gen.scrapers.scraper_base import ScraperBase
from aalto_news_gen.utils.assertion import assert_has_article
from aalto_news_gen.utils.dateparser import DateParser


class ParlamentnilistyScraper(ScraperBase):
    def get_article_text(self, url, soup) -> str:
        article = soup.find('section', class_="article-content")

        article_text = self.get_text(article, remove_img=True)
        assert_has_article(article_text, url)
        return article_text

    def get_date_of_creation(self, soup) -> Optional[datetime]:
        date = soup.find('div', class_='time')

        return DateParser.parse(self.get_text(date, ''))

    def get_html_tags_to_remove(self, soup) -> List[Tag]:
        to_remove = []
        to_remove.extend(soup.find_all('img'))
        to_remove.extend(soup.find_all('section', class_='poll'))
        to_remove.extend(soup.find_all('section', class_='related-articles-wrap'))
        to_remove.extend(soup.find_all('section', class_='in-article'))

        return to_remove
