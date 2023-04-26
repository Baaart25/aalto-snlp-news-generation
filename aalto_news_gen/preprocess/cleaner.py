import glob
from os import path
from pathlib import Path
from typing import List

import pandas as pd
from pandarallel import pandarallel

from aalto_news_gen.utils.config_reader import get_config_from_yaml
from aalto_news_gen.utils.data_helpers import make_dir_if_not_exists
from aalto_news_gen.utils.lang_detector import LanguageDetector
from aalto_news_gen.utils.logger import get_logger
from aalto_news_gen.utils.tokenizer import Tokenizer


class ArticleCleaner:
    def __init__(self, config_path):
        self.config = get_config_from_yaml(config_path)
        self.lang_detector = LanguageDetector(self.config.lang_detector_model_path)
        pandarallel.initialize(nb_workers=self.config.num_process)

    def clean_articles(self, sites):
        all_jsonl_files = glob.glob(f'{self.config.clean_src_dir}/*.jsonl.gz')
        sites_to_clean = all_jsonl_files if sites == 'all' \
            else [x for x in all_jsonl_files if self._is_site_in_sites(Path(x).name, sites.split(','))]

        make_dir_if_not_exists(self.config.clean_out_dir)
        log_file = path.join(self.config.clean_out_dir, 'clean_log.txt')
        logger = get_logger('logger', log_file)
        for site in sites_to_clean:
            self.clean(site, logger)

    def _is_site_in_sites(self, site: str, sites: List[str]):
        for x in sites:
            if x in site:
                return True
        return False

    def clean(self, site, logger):
        df_site = pd.read_json(f'{site}', lines=True)
        logger.info(f'Cleaning {site}, size: {len(df_site)}')

        df_site = df_site[df_site['article'].str.len().between(self.config.min_article_len,
                                                               self.config.max_article_len)]
        logger.info(f'Dropped articles where article is too long or short, size: {len(df_site)}')

        df_site['article_word_cnt'] = df_site.parallel_apply(lambda x: len(x['article'].split()), axis=1)
        df_site = df_site[df_site['article_word_cnt'].between(self.config.min_article_words,
                                                              self.config.max_article_words)]
        logger.info(f'Dropped articles where article is not at least {self.config.min_article_words}'
                    f' words or more that {self.config.max_article_words} words, size: {len(df_site)}')

        df_site['language'] = df_site.apply(lambda x: self.lang_detector.predict(x['article'].replace('\n', ' ')),
                                            axis=1)
        df_site = df_site[(df_site['language'] == 'hu') | (df_site['language'] == 'cs') | (df_site['language'] == 'sk')]
        logger.info(f'Dropped non-Hungarian and non-Czech sentences, size: {len(df_site)}')
        df_site = df_site.drop(columns=['language', 'article_word_cnt'])

        make_dir_if_not_exists(self.config.clean_out_dir)
        domain = self._get_domain_of_site(df_site)
        df_site.to_json(f'{self.config.clean_out_dir}/{domain}.jsonl.gz', orient='records', lines=True,
                        compression='gzip')

    def _get_domain_of_site(self, df):
        return df.iloc[0].domain.split('.')[0]

    def _filter_by_min_article_sentences(self, df):
        return df[df['article'].parallel_map(Tokenizer.count_sentences) >= 3]
