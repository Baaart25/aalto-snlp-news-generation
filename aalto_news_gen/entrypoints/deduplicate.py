import click

from aalto_news_gen.preprocess.deduplicator import Deduplicator


@click.command()
@click.argument('config_path')
def main(config_path):
    deduplicator = Deduplicator(config_path)
    deduplicator.deduplicate()


if __name__ == '__main__':
    main()
