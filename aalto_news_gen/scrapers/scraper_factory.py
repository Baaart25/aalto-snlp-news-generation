from aalto_news_gen.scrapers.ac24_scraper import Ac24Scraper
from aalto_news_gen.scrapers.parlamentnilisty_scraper import ParlamentnilistyScraper
from aalto_news_gen.scrapers.scraper_base import ScraperBase
from aalto_news_gen.scrapers.telex_scraper import TelexScraper
from aalto_news_gen.scrapers.index_scraper import IndexScraper


class HtmlScraperFactory:
    parsers = {
        'telex': TelexScraper,
        'index': IndexScraper,
        'ac24': Ac24Scraper,
        'parlamentnilisty': ParlamentnilistyScraper,
    }

    @classmethod
    def get_parser(cls, site) -> ScraperBase:
        return cls.parsers[site]()
