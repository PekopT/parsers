# coding=utf-8
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

        stock = u'В наличии'

        name = soup.find('h1').text
        if ':' in name:
            names = name.split(':')
            name = names[1]

        image = soup.find('div', 'blok_kartinka').img
        image = image.get('src')
        pictures = [image]

        author = soup.find('meta', {'property': 'og:author'}).get('content')
        isbn = soup.find('meta', {'property': 'og:isbn'}).get('content')
        year = soup.find('meta', {'property': 'og:release_date'}).get('content')
        pages = soup.find('span', 'gray', text=re.compile(u'Страниц')).find_next_sibling('div', 'lpad20')
        publisher = soup.find('span', 'gray', text=re.compile(u'Издательство')).find_next_sibling('div', 'lpad20')
        description = soup.find('p', 'opisanie')
        cover = soup.find('b', {'itemprop': 'bookFormat'})
        cover = cover.text.strip()
        description = description.text.strip()
        publisher = publisher.text.strip()
        pages = pages.text
        price = soup.find('meta', {'itemprop': 'price'}).get('content')
        price = price.split('.')[0]

        also_buy_info = soup.find('table', 'nprn').tr.td.find_all('table')
        also_buy_books = []

        for book in also_buy_info:
            picture_book = book.a.find('img').get('src')
            url_book = book.a.get('href')
            price_info = book.find('b', 'price')
            price_book = re.sub('\D', '', price_info.text).strip()
            name_book = book.find('span', 'f11').a.get_text()

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
            "pages": pages,
            "isbn": isbn,
        }

        if stock:
            row["availability"] = stock

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
            # self.rows_data.append(row)

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