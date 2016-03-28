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

        isbn = book_info.find('b', text=re.compile(u'ISBN'))
        isbn = unicode(isbn.next_sibling).strip()

        year = book_info.find('b', text=re.compile(u'издания'))
        year = unicode(year.next_sibling).strip()

        pages = book_info.find('b', text=re.compile(u'страниц'))
        pages = unicode(pages.next_sibling).strip()

        publisher = book_info.find('b', text=re.compile(u'Издательство'))
        publisher = publisher.find_next_sibling('span').text.strip()

        cover = book_info.find('b', text=re.compile(u'обложки'))
        cover = unicode(cover.next_sibling).strip()

        stock = u'В наличии'

        description = soup.find('span',{'itemprop':'description'})
        if description:
            description = description.text.strip()
        else:
            description = u''


        price_info = book_info.find('div', 'price_block').find('span', {'itemprop': 'price'})
        price = price_info.text.strip()
        price = price.split('.')[0]

        images = soup.find_all('img', 'unselected_img')
        pictures = [img.get('src') for img in images if img]

        also_buy_info = soup.find('td', 'main').find_all('div', 'goods_catalog')
        also_buy_books = []

        for book in also_buy_info:
            picture_book = book.find('td', 'pic_item').find('img').get('src')
            price_info = book.find('div', 'goods_price').text.strip()
            price_book = price_info.split('.')[0]
            price_book = re.sub('\D', '', price_book).strip()
            name_book = book.find('td', 'name_item').text.strip()
            name_book = self.remove_tags(name)
            url_book = book.find('td', 'name_item').a.get('href')

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

        if description:
            row["description"] = description

        if pictures:
            row["images"] = pictures

        if also_buy_books:
            row["also_buy"] = also_buy_books

        self.check_validate_schema(row)
        self.rows_data.append(row)

    def check_validate_schema(self, node):
        f = open('books.schema.json', 'r')
        schema = json.loads(f.read())
        validate(node, schema)

    def close_parser(self):
        sout.write(json.dumps(self.rows_data, ensure_ascii=False))


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
