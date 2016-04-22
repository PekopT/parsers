# -*- coding: utf-8 -*-
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

        author = ''
        author_info = soup.find('div', 'text w_div')
        if author_info:
            author_info = author_info.find('div', 'text')
            if author_info:
                author = author_info.text.replace("\\n","").strip()

        name = ''
        name_info = soup.find('div', 'text w_div')
        if name_info:
            name_info = name_info.h1
            name = name_info.text.strip()

        description = ''
        description_info = soup.find('div', {'id': 'annotation'})
        if description_info:
            description = description_info.text.strip()
            description = description.replace('\t', '').replace('\n', '').replace('\\n', '')

        price = ''
        price_info = soup.find('span', {'id': 'b-price-b'})
        if price_info:
            price = re.sub('\D', '', price_info.text)

        isbn = ''
        isbn_info = soup.find('td', text=re.compile(u'ISBN'))
        if isbn_info:
            isbn = isbn_info.find_next_sibling('td').text.strip()

        publisher = ''
        publisher_info = soup.find('td', text=re.compile(u'Издательство'))
        if publisher_info:
            publisher = publisher_info.find_next_sibling('td').text.strip()

        year = ''
        year_info = soup.find('td', text=re.compile(u'издания'))
        if year_info:
            year = year_info.find_next_sibling('td').text.strip()

        cover = ''
        cover_info = soup.find('td', text=re.compile(u'обложки'))
        if cover_info:
            cover = cover_info.find_next_sibling('td').text.strip()

        pages = ''
        pages_info = soup.find('td', text=re.compile(u'Страниц'))
        if pages_info:
            pages = pages_info.find_next_sibling('td').text.strip()
            pages = re.sub('\D', '', pages)

        pictures = []
        images_info = soup.find('div', 'gallery')
        if images_info:
            images = images_info.find_all('img')
            for img in images:
                pictures.append(img.get('src'))

        stock_info = soup.select("div#row-c table tr td.right div div.text ul li")
        stock = u''
        if stock_info:
            for st in stock_info:
                stock += st.text.strip() + ' , '

        stock = stock.strip(' ,').replace('\t', '').replace('\n', '').replace('\\n', '').replace('\r', '')
        if not stock:
            stock = u'В наличии'

        also_buy_books = []

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
