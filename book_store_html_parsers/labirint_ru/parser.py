# coding=utf-8
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
        name = soup.find('h1').text
        publisher = soup.find('div', 'publisher').text
        publisher = publisher.replace(u'Издательство:', '')
        publishers = publisher.split(',')
        publisher = publishers[0]
        year = publishers[1]
        cover = ''
        isbn = ''
        isbn_info = soup.find('div', 'isbn')
        if isbn_info:
            isbn = isbn_info.text.strip()
            isbn = isbn.replace(u"ISBN:", u"").replace(u"все", "").replace(u"скрыть", "").replace(" ", "").strip()
            isbn = isbn.replace(u'\xa0', '')

        price = soup.find('span', 'buying-price-val-number')
        if not price:
            price = soup.find('span', 'buying-pricenew-val-number')

        if price:
            price = price.text.strip()
            price = re.sub('\D', '', price)
        else:
            price = ''

        description_info = soup.find('div', {'id': 'product-about'})
        if description_info:
            description = description_info.text.strip()
        else:
            description = ''

        pages_info = soup.find('div', 'pages2')
        if pages_info:
            pages = pages_info.text.strip()
            pages = re.sub(u'\D', u'', pages)
        else:
            pages = ''

        year = re.sub(u'\D', u'', year)

        author_info = soup.find('div', 'authors')
        if author_info:
            author_a = author_info.find('a')
            if author_a:
                author = author_a.text.strip()
            else:
                author = author_info.text.strip()
        else:
            author = ''

        stock_info = soup.find('div', 'prodtitle-availibility')
        if stock_info:
            stock = stock_info.span.text.strip()
        else:
            stock = u'В наличии'

        also_buy_info_parent = soup.find('div', {'id': 'product-imho'})
        if also_buy_info_parent:
            also_buy_info = also_buy_info_parent.find_all('div', 'product ')
        else:
            also_buy_info = []

        also_buy_books = []
        for book in also_buy_info:
            img_book = book.find('img', 'book-img-cover').get('data-src')
            name_book_info = book.find('span', 'product-title')
            if name_book_info:
                name_book = name_book_info.text.strip()
            else:
                name_book = ''
            url_book_info = book.find('a', 'cover')
            if url_book_info:
                url_book = url_book_info.get('href')
            else:
                url_book = book.find('a').get('href')

            author_book_info = book.find('div', 'product-author')
            if author_book_info:
                author_book = author_book_info.text.strip()
            else:
                author_book = ''

            price_info = book.find('span', 'price-val')

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

        if pages:
            row["pages"] = pages

        if isbn:
            row["isbn"] = isbn

        if stock:
            row["availability"] = stock

        if cover:
            row["cover"] = cover

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
