from setuptools import setup

setup(
    name='Aalto Czech and Hungarian news generation',
    version='0.1',
    description='',
    url='',
    packages=['aalto_news_gen'],
    license='',
    author='Botond Barta',
    python_requires='',
    install_requires=[
        'setuptools~=65.6.3',
        'typing~=3.7.4.3',
        'tldextract~=3.3.1',
        'beautifulsoup4~=4.11.1',
        # 'warc @ https://github.com/erroneousboat/warc3/archive/master.zip',
        'warc3-wet',
    ]
)
