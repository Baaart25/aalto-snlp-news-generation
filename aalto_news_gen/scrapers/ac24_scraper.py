import copy
from datetime import datetime
from typing import Optional, List

from bs4 import Tag

from aalto_news_gen.scrapers.scraper_base import ScraperBase
from aalto_news_gen.utils.assertion import assert_has_article
from aalto_news_gen.utils.dateparser import DateParser


class Ac24Scraper(ScraperBase):
    def get_article_text(self, url, soup) -> str:
        article = soup.find('div', class_="post-content")
        if not article:
            article = soup.find('div', id="ac24_article")
        if not article:
            article = soup.find('div', class_="component-inner")

        if not article:
            print(1)

        article_text = self.get_text(article, remove_img=True)
        assert_has_article(article_text, url)
        return article_text

    def get_date_of_creation(self, soup) -> Optional[datetime]:
        date = soup.find('time', class_='updated')
        if not date:
            date = soup.find('time', class_='published')

        return DateParser.parse(self.get_text(date, ''))

    def get_html_tags_to_remove(self, soup) -> List[Tag]:
        to_remove = []
        to_remove.extend(soup.find_all('div', class_='adswrapper_post'))
        to_remove.extend(soup.find_all('div', class_='twitter-tweet'))
        to_remove.extend(soup.find_all('div', class_='credits'))
        to_remove.extend(soup.find_all('div', class_='socbuttons'))
        to_remove.extend(soup.find_all('div', class_='jc'))
        to_remove.extend(soup.find_all('spann', class_='formInfo'))
        to_remove.extend(soup.find_all('figure'))
        to_remove.extend(soup.find_all('script'))

        return to_remove
