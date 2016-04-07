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
        value = value.replace(u'\\n', u'').strip()
        return value

    def str_to_int(self, value):
        value = re.sub(u'\D', u'', value)
        return value

    def parse_html(self, data):
        url = data['url']
        html = data['html']
        soup = BeautifulSoup(html, 'html.parser')

        name = soup.h1.text.strip()
        book_info = soup.find('div','b-prew-and-info')

        author = book_info.find('p',text=re.compile(u'Автор')).text
        author = author.replace(u'Автор:','').strip()

        publisher = book_info.find('p',text=re.compile(u'Издательство')).text
        publisher = publisher.replace(u'Издательство:','').strip()
        year = book_info.find('p',text=re.compile(u'Год')).text
        year = year.replace(u'Год:','').strip()

        tab_data = soup.find('div','tabdata')

        cover = tab_data.find(text=re.compile(u'Переплет'))
        cover = cover.replace(u'Переплет:','').strip()

        stock = u'В наличии'

        description = tab_data.find('p').text.strip()

        isbn = tab_data.find('strong',text=re.compile(u'ISBN'))
        if isbn:
            isbn = isbn.next_sibling

        pages = tab_data.find('strong',text=re.compile(u'страниц'))
        if pages:
            pages = pages.next_sibling
            pages = unicode(pages).strip()
            pages = re.sub('\D','', pages)

        images_info = soup.find('div','ins').find_all('img')

        pictures = [img.get('src') for img in images_info if img]

        price_info = soup.find('div','price-info').find('div', 'price-for-us').span
        price = price_info.text.strip()
        price = re.sub('\D','',price)

        also_buy_info = soup.find('div','b-look-often').find_all('li')
        also_buy_books = []

        for book in also_buy_info:
            picture_book = book.find('img').get('src')
            price_info = book.find('div', 'b-price').find('span','new')
            if price_info:
                price_book = price_info.text.strip()
            else:
                price_info = book.find('div','b-price')
                price_book = price_info.text.strip()

            price_book = re.sub('\D', '', price_book).strip()

            name_book = book.find('a','name').text.strip()
            url_book = book.find('a','name').get('href')
            author_info = book.find('div','autor')
            if author_info:
                author_book = author_info.text.strip()
            else:
                author_book = u''

            also_row = {
                "url": url_book,
                "name": name_book,
                "image": picture_book,
                "price": {
                    "currency": "RUR",
                    "type": "currency",
                    "content": int(price_book),
                }
            }

            if author_book:
                also_row["author"] = author_book

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
        }

        if stock:
            row["availability"] = stock

        if pages:
            row["pages"] = pages

        if isbn:
            row["isbn"] = isbn

        if cover:
            row["cover"] = cover

        if pictures:
            row["images"] = pictures

        if also_buy_books:
            row["also_buy"] = also_buy_books

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
