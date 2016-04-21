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

        name_info = soup.h1
        name = name_info.text.strip()

        book_details = soup.find('ul', 'book-detail-params')

        author = book_details.find('li', {'itemprop': 'author'})
        if author:
            author_b = book_details.find('li', {'itemprop': 'author'}).b
            if author_b:
                author_b = author_b.text
                author = author.text.replace(author_b, '').strip()
            else:
                author = author.text

        description_info = soup.find('div', {'itemprop': 'description'})
        if description_info:
            description = description_info.text.strip()
            description = self.remove_tags(description)
        else:
            description = ''

        publisher = u''
        publisher_info = soup.find('span', {'itemprop': 'publisher'})
        if publisher_info:
            publisher = publisher_info.text.strip()

        isbn = u''
        isbn_info = soup.find('span', {'itemprop': 'isbn'})
        if isbn_info:
            isbn = isbn_info.text.strip()

        year = u''
        year_info = soup.find('b', text=re.compile(u'Год'))
        if year_info:
            year = year_info.next_sibling

        cover = u''
        cover_info = soup.find('b', text=re.compile(u'Тип'))

        if cover_info:
            cover = cover_info.next_sibling

        pages = u''
        pages_info = soup.find('span', {'itemprop': 'numberOfPages'})
        if pages_info:
            pages = pages_info.text.strip()


        image_info = soup.find('div', 'book-detail-image').find_all('img')
        pictures = [img.get('src') for img in image_info if img]

        price = ''
        price_info = soup.find('div', {'itemprop': 'price'})
        if price_info:
            price_info = price_info.text.strip()
            price = price_info.split(',')
            price = price[0].strip()

        stock = u'В наличии'
        stock_info = soup.find('li', text=re.compile(u'наличи'))
        if stock_info:
            stock = stock_info.text

        also_buy_info = soup.find('div', 'addition_section').find_all('div', recursive=False)
        also_buy_books = []
        for book in also_buy_info:
            picture_book = book.find('img').get('data-src')
            name_book = book.find('a', 'slick-title').text.strip()
            author_book = book.find('div')
            author_book = author_book.text.strip()
            author_book = self.remove_tags(author_book)
            url_book = book.find('a', 'slick-title').get('href')
            price_book_info = book.find('div','index').text.strip()
            price_book = price_book_info.split(',')[0]
            price_book = price_book.strip()

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
                also_row['author'] = author_book

            also_buy_books.append(also_row)

        row = {
            "url": url,
            "name": name,
        }

        if price:
            row["price"] =  {
                "currency": "RUR",
                "type": "currency",
                "content": int(price)
            }

        if publisher:
            row["publisher"] = publisher

        if author:
            row["author"] = author

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
