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

        author = soup.find('div', 'book-author').find('div', 'h2')
        author = author.text.strip()
        author = author.replace(u'Автор:', '')

        book_info = soup.find('div', 'info2').find('dl')

        isbn = book_info.find('dt', text=re.compile(u'ISBN'))
        if isbn:
            isbn = isbn.findNextSibling('dd')
            isbn = isbn.text.strip()

        pages = book_info.find('dt', text=re.compile(u'Объем'))
        if pages:
            pages = pages.findNextSibling('dd')
            pages = pages.text.strip()

        year = book_info.find('dt', text=re.compile(u'написания'))
        if year:
            year = year.findNextSibling('dd')
            year = year.text

        # pages = book_info.find('dt', text=re.compile(u'Объем')).find_next_sibling('dd')
        # pages = pages.text

        description = soup.find('div', 'book_annotation')
        description = description.text.strip()

        price = soup.find('div', 'book-buy-wrapper').button
        price_text = price.text.strip()

        price = re.sub(u'[А-Я а-яA-Za-z]+', '', price_text).split(',')
        price = re.sub(u'\D', u'', price[0])
        stock = u"На складе"

        row = {}
        row["url"] = url
        row["name"] = name
        row["author"] = author
        row["description"] = description
        row["availability"] = stock
        if isbn:
            row["isbn"] = isbn
        if year:
            row["year"] = year

        row["price"] = {
            "currency": "RUR",
            "type": "currency",
            "content": int(price.strip())
        }

        self.check_validate_schema(row)
        sout.write(json.dumps(row, ensure_ascii=False) + "\n")
        # self.rows_data.append(row)

    def check_validate_schema(self, node):
        f = open('books.schema.json', 'r')
        schema = json.loads(f.read())
        validate(node, schema)

    def close_parser(self):
        pass
        # sout.write(json.dumps(self.rows_data, ensure_ascii=False))


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
