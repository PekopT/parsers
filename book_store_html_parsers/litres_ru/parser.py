# coding=utf-8
import json
import sys
import traceback
import re
from bs4 import BeautifulSoup
from codecs import getwriter
from jsonschema import validate

sout = getwriter("utf-8")(sys.stdout)


class Parser(object):
    rows_data = []

    def remove_tags(self, value):
        value = value.replace(u'\n', u'')
        return value

    def str_to_int(self, value):
        value = re.sub(u'\D', u'', value)
        return value

    def parse_html(self, data):
        url = data['url']
        html = data['html']
        soup = BeautifulSoup(html, 'html.parser')

        name = soup.h1
        name = name.text.strip()

        author = ''
        author_info = soup.find('div', 'book-author')
        if author_info:
            author_info = author_info.find('div', 'h2')
            if author_info:
                author = author_info.text.strip()
                author = author.replace(u'Автор:', '')

        isbn = ''
        pages = ''
        year = ''
        book_info = soup.find('div', 'info2')
        if book_info:
            book_info = book_info.find('dl')
            if book_info:
                isbn = book_info.find('dt', text=re.compile(u'ISBN'))
                if isbn:
                    isbn = isbn.findNextSibling('dd')
                    isbn = isbn.text.strip()

                pages_info = book_info.find('dt', text=re.compile(u'Объем'))
                if pages_info:
                    pages_info = pages_info.findNextSibling('dd')
                    if pages_info:
                        pages = pages_info.text.strip()
                        pages = re.sub('\D','', pages)


                year_info = book_info.find('dt', text=re.compile(u'написания'))
                if year_info:
                    year_info = year_info.findNextSibling('dd')
                    if year_info:
                        year = year_info.text.strip()
                        year = re.sub('\D','', year)

        description = ''
        description_info = soup.find('div', 'book_annotation')
        if description_info:
            description = description_info.text.strip()

        price = ''
        price_info = soup.find('div', 'book-buy-wrapper')
        if price_info:
            price_info = price_info.button
            if price_info:
                price_text = price_info.text.strip()
                price = re.sub(u'[А-Я а-яA-Za-z]+', '', price_text).split(',')
                price = re.sub(u'\D', u'', price[0]).strip()

        stock = u"На складе"

        row = {}
        row["url"] = url
        row["name"] = name
        if author:
            row["author"] = author

        if pages:
            row["pages"] = pages

        if description:
            row["description"] = description

        row["availability"] = stock

        if isbn:
            row["isbn"] = isbn

        if year:
            row["year"] = year

        row["price"] = {
            "currency": "RUR",
            "type": "currency",
            "content": int(price)
        }

        self.check_validate_schema(row)
        sout.write(json.dumps(row, ensure_ascii=False) + "\n")

    def check_validate_schema(self, node):
        f = open('books.schema.json', 'r')
        schema = json.loads(f.read())
        validate(node, schema)

    def close_parser(self):
        pass


def main():
    parser = Parser()
    for line in sys.stdin:
        data = json.loads(line)
        try:
            parser.parse_html(data)
        except Exception as e:
            sys.stderr.write(
                json.dumps({"url": data["url"], "traceback": traceback.format_exc()}, ensure_ascii=False).encode(
                    "utf-8") + "\n")

    parser.close_parser()


if __name__ == '__main__':
    main()
