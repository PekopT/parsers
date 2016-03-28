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

        author = name_info.find_next_sibling('span', 'hChildrenLink').text.strip()
        author = self.remove_tags(author)

        description_info = soup.find('div', {'id': 'textDescriptionId'})
        description = description_info.text.strip()
        description = self.remove_tags(description)

        publisher = u''
        publisher_info = soup.find('span', 'dataName', text=re.compile(u'Издательство')).parent.find_next_sibling('td')
        if publisher_info:
            publisher = publisher_info.text.strip()

        isbn = u''
        isbn_info = soup.find('span', 'dataName', text=re.compile(u'ISBN')).parent.find_next_sibling('td')
        if isbn_info:
            isbn = isbn_info.text.strip()

        year = u''
        year_info = soup.find('span', 'dataName', text=re.compile(u'Год')).parent.find_next_sibling('td')
        if year_info:
            year = year_info.text.strip()

        cover = u''
        cover_info = soup.find('span', 'dataName', text=re.compile(u'Обложка')).parent.find_next_sibling('td')
        if cover_info:
            cover = cover_info.text.strip()

        pages = u''
        pages_info = soup.find('span', 'dataName', text=re.compile(u'Страниц')).parent.find_next_sibling('td')
        if pages_info:
            pages = pages_info.text.strip()

        image_info = soup.find('div', 'podlogkaBig').find_all('img')

        pictures = [img.get('src') for img in image_info if img]
        price_info = soup.find('div', 'priceItemOrange').text.strip()
        price = re.sub('\D','',price_info)

        stock = soup.find('td', 'dataTableNalSpan')
        if stock:
            stock = stock.text.strip()
            stock = self.remove_tags(stock)
        else:
            stock = u'В наличии'

        also_buy_info = soup.find('div', 'catalogSmall').find_all('div', 'item')
        also_buy_books = []

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
            "publisher": publisher,
            "author" : author,
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
