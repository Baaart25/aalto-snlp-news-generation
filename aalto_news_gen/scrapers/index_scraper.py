import copy
from datetime import datetime
from typing import Optional, List

from bs4 import Tag

from aalto_news_gen.errors.invalid_page_error import InvalidPageError
from aalto_news_gen.scrapers.scraper_base import ScraperBase
from aalto_news_gen.utils.assertion import assert_has_article
from aalto_news_gen.utils.dateparser import DateParser


class IndexScraper(ScraperBase):
    def check_page_is_valid(self, url, soup):
        if soup.select('div.pp-article-site'):
            raise InvalidPageError(url, 'Liveblog')

    def get_article_text(self, url, soup) -> str:
        article = copy.copy(soup.find('div', class_="cikk-torzs"))
        # remove lead if exists
        if article:
            leads = article.select('div.cikk-torzs > p > strong')
            for lead in leads:
                lead.decompose()

        if not article:
            article = soup.find('div', class_="text")

        if not article:
            article = soup.find('div', class_='post_text')

        if not article:
            article = soup.find('div', class_="szoveg")

        article_text = self.get_text(article, remove_img=True)
        assert_has_article(article_text, url)
        return article_text

    def get_date_of_creation(self, soup) -> Optional[datetime]:
        date = soup.find('div', class_='datum')
        if not date:
            date = soup.find('time', class_='m-asd_time_date')

        if not date:
            date = soup.find('span', class_='ido')

        date = self.get_text(date, '')
        if 'Módosítva' in date:
            date = date.split("Módosítva")[0].strip()

        return DateParser.parse(self.get_text(date, ''))

    def get_html_tags_to_remove(self, soup) -> List[Tag]:
        to_remove = []
        to_remove.extend(soup.find_all('div', class_='cikk-bottom-text-ad'))
        to_remove.extend(soup.find_all('div', class_='cikk-bottom-box'))
        to_remove.extend(soup.find_all('div', class_='pr__cikk-bottomcontent'))
        to_remove.extend(soup.find_all('nav', class_='pager'))
        to_remove.extend(soup.find_all('div', class_='iframe-embed-container'))
        to_remove.extend(soup.find_all('div', class_='szerkfotogallery'))
        to_remove.extend(soup.find_all('div', class_='szerkfotoimage'))

        to_remove.extend(soup.find_all('div', class_='keretes-donate-doboz'))
        to_remove.extend(soup.find_all('aside', class_='m-automatic-file-snippet'))
        to_remove.extend(soup.find_all('div', class_='m-kepkuldes-box'))
        to_remove.extend(soup.find_all('div', class_='nm_supported__wrapper'))
        to_remove.extend(soup.find_all('div', class_='nm_thanks__wrapper'))
        to_remove.extend(soup.find_all('div', class_='photographer'))

        to_remove.extend(soup.find_all('div', class_='indavideo'))
        to_remove.extend(soup.find_all('div', id='index-social-box'))
        to_remove.extend(soup.find_all('blockquote', class_='tiktok-embed'))
        to_remove.extend(soup.find_all('section', class_='connected'))
        to_remove.extend(soup.find_all('div', class_='post_bottom'))
        to_remove.extend(soup.find_all('div', class_='nm_mini__wrapper'))
        to_remove.extend(soup.find_all('div', class_='table_container'))
        to_remove.extend(soup.find_all('div', class_='szoveg_spec_container'))

        return to_remove