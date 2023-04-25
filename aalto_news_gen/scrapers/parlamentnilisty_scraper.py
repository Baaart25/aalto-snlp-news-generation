import copy
from datetime import datetime
from typing import Optional, List

from bs4 import Tag

from aalto_news_gen.scrapers.scraper_base import ScraperBase
from aalto_news_gen.utils.assertion import assert_has_article
from aalto_news_gen.utils.dateparser import DateParser


class ParlamentnilistyScraper(ScraperBase):
    def get_article_text(self, url, soup) -> str:
        # TODO modify these
        article = soup.find('div', class_="text")

        if not article:
            article = soup.find('div', class_='post_text')

        article_text = self.get_text(article, remove_img=True)
        assert_has_article(article_text, url)
        return article_text

    def get_date_of_creation(self, soup) -> Optional[datetime]:
        # TODO modify these
        date = soup.find('div', class_='date')
        if not date:
            date = soup.find('div', class_='date2')

        return DateParser.parse(date)

    def get_html_tags_to_remove(self, soup) -> List[Tag]:
        to_remove = []

        return to_remove
