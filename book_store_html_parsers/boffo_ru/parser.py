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

    def get_need_element(self, pattern, value):
        dd_string_data = value.split('<br/>')
        for dd_item in dd_string_data:
            if pattern in dd_item.strip():
                return dd_item.strip()
        return False

    def parse_html(self, data):
        url = data['url']
        html = data['html']

        soup = BeautifulSoup(html, 'html.parser')

        images_info = soup.find('span', {'id': 'image-block'})
        pictures = []
        if images_info:
            images_info = images_info.find_all('img')
            pictures = [img.get('src') for img in images_info]

        name = soup.find('h1', 'product_title').text.strip()

        price = ''
        price_info = soup.find('div', 'price')
        if price_info:
            price_info = price_info.find('span', 'current_price')
            if price_info:
                price = price_info.text.strip()
                price = re.sub('\D', '', price)

        book_info = soup.find('dl', 'futures-info clearfix')

        dd = book_info.find('dd')
        dd_string = unicode(dd)
        isbn_info = self.get_need_element(u"ISBN", dd_string)
        pages_info = self.get_need_element(u"стр.", dd_string)

        if isbn_info:
            isbn = isbn_info.replace("ISBN:", "").strip()

        if pages_info:
            pages_info = pages_info.replace('<dd>', '')
            pages_info_data = pages_info.split(',')
            cover_info = pages_info_data[0]
            cover = cover_info.strip()
            pages = pages_info_data[1]
            pages = re.sub('\D', '', pages)

        author = ''
        author_info = soup.find('dt', text=re.compile(u'Автор'))
        if author_info:
            author_info = author_info.find_next_sibling('dd')
            if author_info:
                author = author_info.text.strip()

        year = ''
        publisher = ''
        publisher_info = soup.find('dt', text=re.compile(u'Издательство'))
        if publisher_info:
            publisher_info = publisher_info.find_next_sibling('dd')
            if publisher_info:
                publisher_text = publisher_info.text
                publisher_data = publisher_text.split(',')
                if len(publisher_data) == 2:
                    publisher = publisher_data[0].strip()
                    year = publisher_data[1].strip()
                elif len(publisher_data) == 1:
                    publisher = publisher_data[0].strip()
                    year = ''

                year = re.sub('\D', '', year)

        stock = u"В наличии"

        description = ''
        description_info = soup.find('div', 'text productDescription')
        if description_info:
            description = description_info.text.strip()

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

        if publisher:
            row["publisher"] = publisher

        if description:
            row["description"] = description

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
