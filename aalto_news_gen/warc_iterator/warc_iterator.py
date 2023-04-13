from datetime import datetime
from typing import Iterator

import tldextract
import warc

from aalto_news_gen.data_models.page import Page


class WarcIterator:

    def iter_pages(self, file) -> Iterator[Page]:
        warc_file = warc.open(file)
        for record in warc_file:
            url = record['WARC-Target-URI']
            date = datetime.strptime(record['WARC-Date'], '%Y-%m-%dT%H:%M:%SZ')
            html_header, html_text = record.payload.read().split(b'\r\n\r\n', maxsplit=1)
            ext = tldextract.extract(url)
            domain = f'{ext.domain}.{ext.suffix}'
            try:
                yield Page(url, domain, date, html_text.decode('utf-8'))
            except:
                yield Page(url, domain, date, html_text.decode('latin-1'))
