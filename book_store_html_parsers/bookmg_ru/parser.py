# -*- coding: utf-8 -*-
import sys
import json
import traceback
import re
from codecs import getwriter
from bs4 import BeautifulSoup
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

        isbn_info = soup.find('td', text=re.compile(u'ISBN'))
        if isbn_info:
            isbn = isbn_info.find_next_sibling('td').text.strip()
        else:
            isbn = u''

        publisher_info = soup.find('td', text=re.compile(u'издательство'))
        if publisher_info:
            publisher = publisher_info.find_next_sibling('td').text.strip()
        else:
            publisher = u''

        year_info = soup.find('td', text=re.compile(u'год'))
        if year_info:
            year = year_info.find_next_sibling('td').text.strip()
        else:
            year = u''

        cover_info = soup.find('td', text=re.compile(u'выпуска'))
        if cover_info:
            cover = cover_info.find_next_sibling('td').text.strip()
        else:
            cover = u''

        pages_info = soup.find('td', text=re.compile(u'страниц'))
        if pages_info:
            pages = pages_info.find_next_sibling('td').text.strip()
        else:
            pages = u''

        image = soup.find('meta', {'property': 'og:image'}).get('content')

        description = soup.find('meta', {'property': 'og:description'}).get('content')

        author_info = soup.find('h2', 'b-author-div')
        name = author_info.h1.text

        author = author_info.text.replace(name, '').strip()
        name = name.strip()

        author = author.replace('\\n', '').replace('\r', '')
        author = author.strip('. ')

        price_info = soup.find('div', 'price2')

        stock_info = price_info.find_next_sibling('div', 'news_div').div.div
        stock = stock_info.text.strip()

        price = re.sub(u'\D', '', price_info.text)
        pictures = [image]
        year = re.sub(u'\D', '', year).strip()

        also_buy_books = []

        row = {
            "url": url,
            "name": name,
            "author": author,
            "description": description,
            "price": {
                "currency": "RUR",
                "type": "currency",
                "content": int(price)
            },
        }

        if publisher:
            row["publisher"] = publisher

        if year:
            row["year"] = year

        if pages:
            row["pages"] = pages

        if isbn:
            row["isbn"] = isbn

        if stock:
            row["availability"] = stock

        if cover:
            row["cover"] = cover

        if also_buy_books:
            row["also_buy"] = also_buy_books

        if pictures:
            row["images"] = pictures

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
