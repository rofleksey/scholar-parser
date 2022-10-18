import argparse
import json
import urllib.parse
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup

ARTICLE_SELECTOR = '#gs_res_ccl_mid > .gs_scl'
ARTICLE_NAME_SELECTOR = '.gs_ri > .gs_rt > a'
ARTICLE_AUTHOR_SELECTOR = '.gs_ri > .gs_a'
ARTICLE_ANNOTATION_SELECTOR = '.gs_ri > .gs_rs'


@dataclass
class Article:
    """Class representing a single article"""
    name: str
    link: str
    author: str
    annotation: str


def fetch_articles(query, page):
    base_url = 'https://scholar.google.com/scholar?'
    params = {'hl': 'en', 'start': 10 * (page - 1), 'q': query}
    url = f'{base_url}{urllib.parse.urlencode(params)}'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    articles = soup.select(ARTICLE_SELECTOR)
    result = []
    for article_div in articles:
        name_div = article_div.select_one(ARTICLE_NAME_SELECTOR)
        name = name_div.get_text()
        link = name_div['href']
        author = article_div.select_one(ARTICLE_AUTHOR_SELECTOR).get_text()
        annotation = article_div.select_one(ARTICLE_ANNOTATION_SELECTOR).get_text()
        result.append(Article(name, link, author, annotation))
    return result


cli = argparse.ArgumentParser(description='Parse articles from scholar.google.com. Output as JSON to stdout or file.')
cli.add_argument('-q', '--query', help='query text', required=True)
cli.add_argument('-o', '--output', help='output file (or print to console if not set)', default=None)
cli.add_argument('-p', '--pages', help='number of pages to query and parse', type=int, default=1)
args = cli.parse_args()

output_articles = []
for i in range(1, args.pages + 1):
    output_articles.extend(fetch_articles(args.query, i))

if args.output:
    with open(args.output, 'w') as outfile:
        json.dump(output_articles, outfile, default=vars, indent=2)
else:
    print(json.dumps(output_articles, default=vars, indent=2))
