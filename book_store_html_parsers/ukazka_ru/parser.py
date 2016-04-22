# coding=utf-8
import sys
import json
import traceback
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

        pictures = []
        image_info = soup.find('div', 'blok_kartinka')
        if image_info:
            image = image_info.get('src')
            pictures = [image]

        author = ''
        author_info = soup.find('meta', {'property': 'og:author'})
        if author_info:
            author = author_info.get('content')

        isbn = ''
        isbn_info = soup.find('meta', {'property': 'og:isbn'})
        if isbn_info:
            isbn = isbn_info.get('content')

        year = ''
        year_info = soup.find('meta', {'property': 'og:release_date'})
        if year_info:
            year = year_info.get('content')
            year = re.sub('\D', '', year)

        pages = ''
        pages_info = soup.find('span', 'gray', text=re.compile(u'Страниц'))
        if pages_info:
            pages_info = pages_info.find_next_sibling('div', 'lpad20')
            if pages_info:
                pages = pages.text.strip()
                pages = re.sub('\D', '', pages)

        cover = ''
        cover_info = soup.find('b', {'itemprop': 'bookFormat'})
        if cover_info:
            cover = cover.text.strip()

        description = ''
        description_info = soup.find('p', 'opisanie')
        if description_info:
            description = description.text.strip()

        publisher = ''
        publisher_info = soup.find('span', 'gray', text=re.compile(u'Издательство'))
        if publisher_info:
            publisher_info = publisher_info.find_next_sibling('div', 'lpad20')
            publisher = publisher_info.text.strip()


        price = ''
        price_info = soup.find('meta', {'itemprop': 'price'}).get('content')
        if price_info:
            price = price_info.split('.')[0]
            price = re.sub('\D', '', price)

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
            "name": name

        }

        if price:
            row["price"] =  {
                "currency": "RUR",
                "type": "currency",
                "content": int(price)
        }

        if description:
            row["description"] = description

        if author:
            row["author"] = author

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
