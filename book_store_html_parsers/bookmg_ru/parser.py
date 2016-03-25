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


        isbn_info = soup.find('td', text=re.compile(u'ISBN'))
        isbn = isbn_info.find_next_sibling('td').text.strip()

        publisher_info = soup.find('td', text=re.compile(u'издательство'))
        publisher = publisher_info.find_next_sibling('td').text.strip()

        year_info = soup.find('td', text=re.compile(u'год'))
        year = year_info.find_next_sibling('td').text.strip()


        cover_info = soup.find('td', text=re.compile(u'выпуска'))
        cover = cover_info.find_next_sibling('td').text.strip()


        pages_info = soup.find('td', text=re.compile(u'страниц'))
        pages = pages_info.find_next_sibling('td').text.strip()


        image = soup.find('meta', {'property':'og:image'}).get('content')

        description = soup.find('meta', {'property':'og:description'}).get('content')

        author_info = soup.find('h2','b-author-div')
        name = author_info.h1.text

        author = author_info.text.replace(name, '').strip()
        name = name.strip()

        author = author.replace('\\n','').replace('\r','')
        author = author.strip('. ')



        price_info = soup.find('div','price2')
        price = price_info.text

        stock_info = price_info.find_next_sibling('div','news_div').div.div
        stock = stock_info.text.strip()

        price = re.sub(u'\D', '', price_info.text)
        pictures = [image]
        year = re.sub(u'\D', '', year).strip()

        also_buy_books = []

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
