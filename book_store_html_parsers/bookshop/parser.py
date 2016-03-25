# -*- coding: utf-8 -*-
import sys
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

        item_info_section = soup.find('table', 'item_info_section')

        isbn = u''
        isbn_info = item_info_section.find('td', text=re.compile(u'ISBN'))
        if isbn_info:
            isbn = isbn_info.find_next_sibling('td').text.strip()

        year = u''
        year_info = item_info_section.find('td', text=re.compile(u'Год'))
        if year_info:
            year = year_info.find_next_sibling('td').text.strip()
            year = re.sub('\D', '', year)

        publisher = u''
        publisher_info = item_info_section.find('td', text=re.compile(u'Издательство'))
        if publisher_info:
            publisher = publisher_info.find_next_sibling('td').text.strip()

        author = u''
        author_info = item_info_section.find('td', text=re.compile(u'Автор'))
        if author_info:
            author = author_info.find_next_sibling('td').text.strip()

        cover = u''
        cover_info = item_info_section.find('td', text=re.compile(u'Переплет'))
        if cover_info:
            cover = cover_info.find_next_sibling('td').text.strip()

        pages_info = item_info_section.find('td', text=re.compile(u'страниц'))
        if pages_info:
            pages = pages_info.find_next_sibling('td').text.strip()
        else:
            pages = u''

        price_info = soup.find('div', 'item_price').find('div', 'item_current_price')
        price = re.sub('\D', '', price_info.text)

        description = soup.find('div', 'bx_item_description').text.strip()
        description = description.replace('\n','').replace('\r','')

        name = soup.h1.text.strip()

        image_info = soup.find('div', 'bx_item_slider')
        image = image_info.find('img').get('src')
        pictures = [image]
        # pictures = []

        stock = u'В Наличии'

        also_buy_info = soup.find('div', 'bx_item_list_section').find_all('div', 'bx_catalog_item')
        also_buy_books = []
        for book in also_buy_info:
            picture_book_data = book.a.get('style').split(':')
            picture_book = picture_book_data[1].strip().replace('url(', '').replace(')', '')

            price_info = book.find('div', 'bx_catalog_item_price')
            price_book = re.sub('\D', '', price_info.text).strip()

            name_book = book.find('div', 'bx_catalog_item_title').text.strip()
            url_book = book.a.get('href')

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
            "isbn": isbn,
        }

        if stock:
            row["availability"] = stock

        if pages:
            row["pages"] = pages

        if cover:
            row["cover"] = cover

        if also_buy_books:
            row["also_buy"] = also_buy_books

        if pictures:
            row["images"] = pictures


        try:
            self.check_validate_schema(row)
            self.rows_data.append(row)
        except Exception as e:
            print e.message

    def check_validate_schema(self, node):
        f = open('books.schema.json', 'r')
        schema = json.loads(f.read())
        validate(node, schema)

    def close_parser(self):
        sout.write(json.dumps(self.rows_data, ensure_ascii=False))


def main():
    parser = Parser()
    for line in sys.stdin:
        try:
            data = json.loads(line)
            try:
                parser.parse_html(data)
            except Exception as e:
                print str(e)
        except Exception as e:
            print str(e)

    parser.close_parser()


if __name__ == '__main__':
    main()
