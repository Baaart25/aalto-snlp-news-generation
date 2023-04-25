from datetime import datetime
from typing import Optional, List

from bs4 import Tag

from aalto_news_gen.errors.invalid_page_error import InvalidPageError
from aalto_news_gen.scrapers.scraper_base import ScraperBase
from aalto_news_gen.utils.assertion import assert_has_article
from aalto_news_gen.utils.dateparser import DateParser


class TelexScraper(ScraperBase):

    def check_page_is_valid(self, url, soup):
        if soup.select('div.liveblog'):
            raise InvalidPageError(url, 'Liveblog')

    def get_article_text(self, url, soup) -> str:
        article = soup.find('div', class_="article-html-content")

        article_text = self.get_text(article, remove_img=True)
        assert_has_article(article_text, url)
        return article_text

    def get_date_of_creation(self, soup) -> Optional[datetime]:
        date = soup.find('p', class_='history--original')

        if not date:
            date = soup.find('p', id='original_date')

        if not date:
            date = soup.find('div', class_='article_date')
            date_object = DateParser.parse(self.get_text(date, '').split('\n')[0])
            if date_object:
                return date_object

        return DateParser.parse(self.get_text(date, ''))


    def get_html_tags_to_remove(self, soup) -> List[Tag]:
        to_remove = []
        to_remove.extend(soup.find_all('div', class_='long-img'))
        to_remove.extend(soup.find_all('figure', class_='media'))
        to_remove.extend(soup.find_all('figure', class_='image'))
        to_remove.extend(soup.find_all('div', class_='article-endbox-campaign-content'))
        # Ide kattintva olvashatók a Telex legfrissebb hírei. / > > > > A Telex legfrissebb híreit itt találja > > > >
        to_remove.extend(soup.select('p > a[href="/legfrissebb"] > strong'))

        return to_remove
