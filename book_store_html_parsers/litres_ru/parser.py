# -*- coding: utf-8 -*-

import sys
import json
import re
from codecs import getwriter
from bs4 import BeautifulSoup

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

        info = soup.body

        name = soup.h1
        name = name.text.strip()

        author = soup.find('div', 'book-author').find('div', 'h2')
        author = author.text.strip()
        author = author.replace(u'Автор:', '')

        book_info = soup.find('div', 'info2').find('dl')

        isbn = book_info.find('dt', text=re.compile('ISBN')).findNextSibling('dd')
        isbn = isbn.text

        year = book_info.find('dt', text=re.compile(u'написания')).findNextSibling('dd')
        year = year.text

        pages = book_info.find('dt', text=re.compile(u'Объем')).find_next_sibling('dd')
        pages = pages.text

        description = soup.find('div', 'book_annotation')
        description = description.text.strip()

        price = soup.find('div', 'book-buy-wrapper').button
        price_text = price.text.strip()

        price = re.sub(u'[А-Я а-яA-Za-z]+', '', price_text).split(',')
        price = price[0]
        stock = u"На складе"

        row = {}
        row["url"] = url
        row["name"] = name
        row["author"] = author
        row["description"] = description
        row["availability"] = stock
        row["isbn"] = isbn
        row["year"] = year
        row["price"] = {
            "currency": "RUR",
            "type": "currency",
            "content": price
        }

        self.rows_data.append(row)

    def check_validate_schema(self):
        pass

    def close_parser(self):
        sout.write(json.dumps(self.rows_data, ensure_ascii=False))


def main():
    parser = Parser()
    for line in sys.stdin:
        try:
            data = json.loads(line)
            try:
                parser.parse_html(data)
            except Exception:
                pass
        except Exception:
            pass

    parser.close_parser()


if __name__ == '__main__':
    main()
