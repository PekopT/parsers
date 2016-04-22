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

        price = ''
        price_info = soup.find('div', 'item_price')
        if price_info:
            price_info = price_info.find('div', 'item_current_price')
            price = re.sub('\D', '', price_info.text)

        description_info = soup.find('div', 'bx_item_description')
        if description_info:
            description = description_info.text.strip()
            description = description.replace(u"Полное описание","").replace('\n', '').replace("\\n","").replace('\r', '').strip()

        name = soup.h1.text.strip()
        name = name.replace("\\n","").strip()

        pictures = []
        image_info = soup.find('div', 'bx_item_slider')
        if image_info:
            image_info = image_info.find('img')
            if image_info:
                image = image_info.get('src')
                pictures = [image]

        stock = u'В Наличии'
        also_buy_info = soup.find('div', 'bx_item_list_section')
        if also_buy_info:
            also_buy_info = also_buy_info.find_all('div', 'bx_catalog_item')

        also_buy_books = []

        if also_buy_info:
            for book in also_buy_info:
                picture_book_data = book.a.get('style').split(':')
                picture_book = picture_book_data[1].strip().replace('url(', '').replace(')', '')

                price_info = book.find('div', 'bx_catalog_item_price')
                if price_info:
                    price_book = re.sub('\D', '', price_info.text).strip()
                else:
                    price_book = ''

                name_book = book.find('div', 'bx_catalog_item_title').text.strip()
                url_book = book.a.get('href')

                also_row = {
                    "url": url_book,
                    "name": name_book,
                    "image": picture_book
                }

                if price_book:
                    also_row["price"] = {
                        "currency": "RUR",
                        "type": "currency",
                        "content": int(price_book),
                    }

                also_buy_books.append(also_row)

        row = {
            "url": url,
            "name": name
        }

        if price:
            row["price"] = {
                "currency": "RUR",
                "type": "currency",
                "content": int(price)
            }

        if author:
            row["author"] = author

        if description:
            row["description"] = description

        if publisher:
            row["publisher"] = publisher

        if year:
            row["year"] = year

        if isbn:
            row["isbn"] = isbn

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
