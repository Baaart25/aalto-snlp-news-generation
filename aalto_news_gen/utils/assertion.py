from aalto_news_gen.errors.missing_article_error import MissingArticleError


def assert_has_article(article, url):
    if not article or not article.strip():
        raise MissingArticleError(url)


