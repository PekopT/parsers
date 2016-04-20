# -*- coding: utf-8 -*-
import sys
import json
import re
import traceback
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

        name = soup.h1
        name = name.text.replace('\\n', '').strip()

        isbn_li = soup.find('ul', 'isbn-list').find('li', 'first')
        isbn = isbn_li.find('span')
        isbn = isbn.text.strip()

        pages_info = isbn_li.findNextSibling('li')
        pages = pages_info.text.strip()

        pages = re.sub('\D', '', pages)

        year = pages_info.findNextSibling('li')
        year = year.text.strip()
        year = re.sub('\D', '', year)

        author = soup.find('p', 'author')
        author = author.text.replace('\\n', '').strip()

        price_info = soup.find('div', 'yprice price')
        price = price_info.text

        price = self.str_to_int(price)

        description_info = soup.find('div', 'note')
        description = description_info.text.replace('\\n', '').strip()

        price_currency = "RUR"
        stock = u'На складе'
        cover_info = soup.find('td', text=re.compile(u'Обложка')).findNextSibling('td')
        cover = cover_info.text.strip()

        publisher_info = soup.find('td', text=re.compile(u'Издательство')).findNextSibling('td')
        publisher = publisher_info.text.strip()

        also_buy_info = soup.select("div#slider > table  tbody > tr.cover > td")
        also_buy_info_title = soup.select("div#slider > table  tbody  tr.title > td")
        also_buy_books = []

        book_item = 0
        if also_buy_info:
            for book in also_buy_info:
                img_book = book.find('img').get('src')
                name_book = book.find('img').get('title')
                url_book = book.find('a').get('href')
                price_info = also_buy_info_title[book_item].find('span', 'price')
                author_book_info = also_buy_info_title[book_item].find_all('a', 'color-blue')

                if author_book_info:
                    author_book = ','.join([auth.text for auth in author_book_info if auth])
                else:
                    author_book = ''

                if price_info:
                    price_book = price_info.text
                    price_book = re.sub('\D', '', price_book)
                else:
                    price_book = ''

                also_row = {}

                if img_book:
                    also_row["image"] = img_book

                if name_book:
                    also_row["name"] = name_book

                if url_book:
                    also_row["url"] = url_book

                if author_book:
                    also_row["author"] = author_book

                if price_book:
                    also_row["price"] = {
                        "currency": "RUR",
                        "type": "currency",
                        "content": int(price_book),
                    }

                also_buy_books.append(also_row)
                book_item += 1

        row = {
            "url": url,
            "name": name
        }

        if author:
            row["author"] = author

        if publisher:
            row["publisher"] = publisher

        if description:
            row["description"] = description

        if price:
            row["price"] = {
                "currency": price_currency,
                "type": "currency",
                "content": int(price)
            }

        row["availability"] = stock

        if year:
            row["year"] = year

        if cover:
            row["cover"] = cover

        if pages:
            row["pages"] = pages

        if isbn:
            row["isbn"] = isbn

        if also_buy_books:
            row["also_buy"] = also_buy_books

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
