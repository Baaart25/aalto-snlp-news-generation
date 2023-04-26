import click

from aalto_news_gen.models.bert2bert import Bert2Bert


@click.command()
@click.argument('config_path')
def main(config_path):
    model = Bert2Bert(config_path)
    model.train()


if __name__ == '__main__':
    main()
