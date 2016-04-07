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

        author = soup.find('div', 'text w_div').find('div', 'text').text

        name_info = soup.find('div', 'text w_div').h1
        name = name_info.text.strip()

        description_info = soup.find('div', {'id': 'annotation'})
        description = description_info.text.strip()
        description = description.replace('\t', '').replace('\n', '').replace('\\n', '')

        price_info = soup.find('span', {'id': 'b-price-b'})
        price = re.sub('\D', '', price_info.text)

        isbn_info = soup.find('td', text=re.compile(u'ISBN'))
        isbn = isbn_info.find_next_sibling('td').text.strip()

        publisher_info = soup.find('td', text=re.compile(u'Издательство'))
        publisher = publisher_info.find_next_sibling('td').text.strip()

        year_info = soup.find('td', text=re.compile(u'издания'))
        year = year_info.find_next_sibling('td').text.strip()

        cover_info = soup.find('td', text=re.compile(u'обложки'))
        cover = cover_info.find_next_sibling('td').text.strip()

        pages_info = soup.find('td', text=re.compile(u'Страниц'))
        pages = pages_info.find_next_sibling('td').text.strip()
        pages = re.sub('\D', '', pages)

        images = soup.find('div', 'gallery').find_all('img')
        pictures = []
        for img in images:
            pictures.append(img.get('src'))

        stock_info = soup.select("div#row-c table tr td.right div div.text ul li")
        stock = u''
        for st in stock_info:
            stock += st.text.strip() + ' , '

        stock = stock.strip(' ,').replace('\t', '').replace('\n', '').replace('\\n', '').replace('\r', '')

        also_buy_books = []

        row = {
            "url": url,
            "name": name,
            "price": {
                "currency": "RUR",
                "type": "currency",
                "content": int(price)
            },
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
        # self.rows_data.append(row)


    def check_validate_schema(self, node):
        f = open('books.schema.json', 'r')
        schema = json.loads(f.read())
        validate(node, schema)

    def close_parser(self):
        pass
        # sout.write(json.dumps(self.rows_data, ensure_ascii=False))


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
