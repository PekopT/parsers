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

        author = ''
        author_info = name_info.find_next_sibling('span', 'hChildrenLink')
        if author_info:
            author = author_info.text.strip()
            author = self.remove_tags(author)

        description_info = soup.find('div', {'id': 'textDescriptionId'})
        if description_info:
            description = description_info.text.strip()
            description = self.remove_tags(description)
        else:
            description = ''

        publisher = u''
        publisher_info = soup.find('span', 'dataName', text=re.compile(u'Издательство'))

        if publisher_info:
            publisher_info = publisher_info.parent.find_next_sibling('td')
            if publisher_info:
                publisher = publisher_info.text.strip()

        isbn = u''
        isbn_info = soup.find('span', 'dataName', text=re.compile(u'ISBN'))
        if isbn_info:
            isbn_info = isbn_info.parent.find_next_sibling('td')
            if isbn_info:
                isbn = isbn_info.text.strip()

        year = u''
        year_info = soup.find('span', 'dataName', text=re.compile(u'Год'))
        if year_info:
            year_info = year_info.parent.find_next_sibling('td')
            if year_info:
                year = year_info.text.strip()

        cover = u''
        cover_info = soup.find('span', 'dataName', text=re.compile(u'Обложка'))
        if cover_info:
            cover_info = cover_info.parent.find_next_sibling('td')
            if cover_info:
                cover = cover_info.text.strip()

        pages = u''
        pages_info = soup.find('span', 'dataName', text=re.compile(u'Страниц'))
        if pages_info:
            pages_info = pages_info.parent.find_next_sibling('td')
            if pages_info:
                pages = pages_info.text.strip()

        pictures = []
        image_info = soup.find('div', 'podlogkaBig')
        if image_info:
            image_info = image_info.find_all('img')
            pictures = [img.get('src') for img in image_info if img]

        price_info = soup.find('div', 'priceItemOrange')
        if price_info:
            price_info = price_info.text.strip()
            price = re.sub('\D','',price_info)

        stock = soup.find('td', 'dataTableNalSpan')
        if stock:
            stock = stock.text.strip()
            stock = self.remove_tags(stock)
        else:
            stock = u'В наличии'

        also_buy_info = soup.find('div', 'catalogSmall')
        if also_buy_info:
            also_buy_info = also_buy_info.find_all('div', 'item')
        also_buy_books = []
        if not also_buy_info:
            also_buy_info = []

        for book in also_buy_info:
            picture_book = book.find('img').get('src')
            name_book = book.find('img').get('title')
            author_book = book.find('span', 'authorsBook')
            if author_book:
                author_book = author_book.text.strip()
            url_book = book.a.get('href')
            price_book = book.find('div', 'priceItem').text.strip()
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
            "price": {
                "currency": "RUR",
                "type": "currency",
                "content": int(price)
            },
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
