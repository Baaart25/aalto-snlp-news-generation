import glob
import multiprocessing as mp
from os import listdir, path
from typing import Iterable, Optional

import click
from multiprocessing_logging import install_mp_handler
from tqdm import tqdm

from aalto_news_gen.errors.page_error import PageError
from aalto_news_gen.scrapers.scraper_factory import HtmlScraperFactory
from aalto_news_gen.data_models.article import Article
from aalto_news_gen.data_models.page import Page
from aalto_news_gen.serializers.article_serializer import ArticleSerializer
from aalto_news_gen.utils.data_helpers import make_dir_if_not_exists
from aalto_news_gen.utils.logger import get_logger
from aalto_news_gen.warc_iterator.warc_iterator import WarcIterator


@click.command()
@click.argument('src_directory')
@click.argument('out_directory')
@click.option('--num_process', default=1, type=click.INT)
@click.option('--sites', default='all', help='Sites to scrape, separated by commas')
def main(src_directory, out_directory, num_process, sites):
    warc_parser = WarcIterator('bad_index.txt')

    make_dir_if_not_exists(out_directory)

    sites_to_scrape = listdir(src_directory) if sites == 'all' else sites.split(',')
    for site in sites_to_scrape:
        log_file = f'{path.join(out_directory, site)}_log.txt'
        logger = get_logger(site, log_file)

        file_to_save_to = path.join(out_directory, f'{site}.jsonl.gz')

        parser = HtmlScraperFactory.get_parser(site)

        logger.info(f'Started processing pages for: {site} with {type(parser).__name__}')

        subdirectory = path.join(src_directory, f'{site}/cc_downloaded')
        files_to_scrape = set(listdir(subdirectory))
        for file_name in files_to_scrape:
            articles = []
            logger.info(f'Parsing file: {file_name}')
            file_path = path.join(subdirectory, file_name)
            if num_process <= 1:
                for page in tqdm(warc_parser.iter_pages(file_path)):
                    article = process_page((page, parser, logger))
                    if article:
                        articles.append(article)
            else:
                pbar = tqdm()
                install_mp_handler()
                proc_pool = mp.Pool(num_process)
                for result in proc_pool.imap_unordered(process_page,
                                                       iter_pages_with_args(warc_parser.iter_pages(file_path),
                                                                            parser,
                                                                            logger)):
                    if result:
                        articles.append(result)
                    pbar.update()

                proc_pool.close()
                proc_pool.join()
                pbar.close()
            ArticleSerializer.serialize_articles(file_to_save_to, articles)
            logger.info(f'Parsed file: {file_name}')


def iter_pages_with_args(iterator: Iterable[Page], parser, logging):
    for page in iterator:
        yield page, parser, logging


def process_page(params) -> Optional[Article]:
    (page, parser, logger) = params
    try:
        article = parser.get_article(page)
        return article
    except PageError as e:
        logger.warning(e)
    except Exception as e:
        logger.exception(e, f'in {page.url}')
    return None


if __name__ == '__main__':
    main()
