# -*- coding: utf-8 -*-
import sys
import traceback
import json
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

        name_info = soup.h1
        name = name_info.text.strip()

        author = name_info.find_next_sibling('h2').text.strip()

        details_info = soup.find('div', {'id': 'details_info_product'})
        description_info = details_info.find_all('div', 'description')

        if len(description_info) == 2:
            description = description_info[len(description_info) - 1].text.strip()

        price_info = details_info.find('div', 'price')
        price = re.sub(u'\D', '', price_info.text)

        stock = details_info.find('div', "availability").find('div', 'value').text.strip()

        product_details_text = details_info.find('div', {'id': 'product_details_text'}).find('div', 'extendedDetails')

        isbn_info = product_details_text.find('span', text=re.compile(u'ISBN'))
        isbn = isbn_info.parent.text.replace(isbn_info.text, '')

        pages_info = product_details_text.find('span', text=re.compile(u'Количество'))
        cover_info = product_details_text.find('span', text=re.compile(u'переплет'))

        pages = pages_info.parent.text.replace(pages_info.text, '')
        cover = cover_info.parent.text.replace(cover_info.text, '')

        image = details_info.find('img').get('src')
        pictures = [image]

        short_details = details_info.find('div', 'shortDetails').text
        short_details_data = short_details.split(',')

        year = short_details_data[len(short_details_data) - 1]
        year = re.sub(u'\D', '', year).strip()

        publisher = ','.join(short_details_data[:len(short_details_data) - 2])

        publisher = publisher.strip()

        also_buy_info = soup.find('div', {'id': 'orderedWithProducts'}).find_all('div', 'product book')
        also_buy_books = []

        for book in also_buy_info:
            price_info = book.find('div', 'price').span
            price_book = re.sub('\D', '', price_info.text).strip()

            name_book = book.find('div', 'title').find('p', 'name').text.strip()
            author_book = book.find('div', 'title').text.strip()
            author_book = author_book.replace(name_book, '').strip()
            url_book = book.find('div', 'title').find('p', 'name').a.get('href')

            also_row = {
                "url": url_book,
                "name": name_book,
                # "image": picture_book,
                "price": {
                    "currency": "RUR",
                    "type": "currency",
                    "content": int(price_book),
                }
            }

            also_buy_books.append(also_row)

        row = {
            "url": url,
            "name": name,
            "publisher": publisher,
            "author": author,

            "description": description,
            "price": {
                "currency": "RUR",
                "type": "currency",
                "content": int(price)
            },
            "year": year,
            "pages": pages,
            "isbn": isbn,
        }

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
