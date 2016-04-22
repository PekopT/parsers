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
        book_info = soup.find('td', 'descr')
        if book_info:
            isbn = ''
            isbn_info = book_info.find('span',{'itemprop':'isbn'})
            if isbn_info:
                isbn = isbn_info.text.strip()
            else:
                isbn_info = book_info.find('b', text=re.compile(u'ISBN'))
                if isbn_info:
                    isbn = unicode(isbn_info.next_sibling).strip()

            year = book_info.find('b', text=re.compile(u'издания'))
            if year:
                year = unicode(year.next_sibling).strip()

            pages = ''
            pages_info = book_info.find('b', text=re.compile(u'страниц'))
            if pages_info:
                pages = unicode(pages.next_sibling).strip()

            publisher = ''
            publisher_info = book_info.find('b', text=re.compile(u'Издательство'))
            if publisher_info:
                publisher = publisher.find_next_sibling('span').text.strip()

            cover = ''
            cover_info = book_info.find('b', text=re.compile(u'обложки'))
            if cover_info:
                cover = unicode(cover_info.next_sibling).strip()

        stock = u'В наличии'

        description = soup.find('span',{'itemprop':'description'})
        if description:
            description = description.text.strip()
        else:
            description = u''

        price = ''
        price_info = book_info.find('div', 'price_block')
        if price_info:
            price_info = price_info.find('span', {'itemprop': 'price'})
            if price_info:
                price = price_info.text.strip()
                price = price.split('.')[0]
                price = re.sub('\D', '', price)

        images = soup.find_all('img', 'unselected_img')
        pictures = [img.get('src') for img in images if img]

        also_buy_info = soup.find('td', 'main')
        if also_buy_info:
            also_buy_info = also_buy_info.find_all('div', 'goods_catalog')

        if not also_buy_info:
            also_buy_info = []

        also_buy_books = []

        for book in also_buy_info:
            picture_book = book.find('td', 'pic_item').find('img').get('src')
            price_info = book.find('div', 'goods_price')
            if price_info:
                price_book = price_info.text.strip().split('.')[0]
                price_book = re.sub('\D', '', price_book).strip()
            else:
                price_book = ''

            name_book_info = book.find('td', 'name_item')
            if name_book_info:
                name_book = name_book_info.text.strip()
                name_book = self.remove_tags(name_book)
            else:
                name_book = ''
            url_book = book.find('td', 'name_item').a.get('href')

            also_row = {}
            also_row["url"] = url_book

            if name_book:
                also_row["name"] = name_book

            if picture_book:
                also_row["image"] = picture_book

            if price_book:
                also_row["price"] =  {
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
            row["price"] =  {
                "currency": "RUR",
                "type": "currency",
                "content": int(price)
            }

        if isbn:
            row["isbn"] = isbn

        if stock:
            row["availability"] = stock

        if publisher:
            row["publisher"] = publisher

        if cover:
            row["cover"] = cover

        if pages:
            row["pages"] = pages

        if year:
            row["year"] = year

        if description:
            row["description"] = description

        if pictures:
            row["images"] = pictures

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
