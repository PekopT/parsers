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

        name = soup.h1.text
        name = self.remove_tags(name)

        author = ''
        author_info = soup.find('h2', {'itemprop': 'author'})
        if author_info:
            author = self.remove_tags(author_info.text)

        price = ''
        price_info = soup.find('span', {'itemprop': 'price'})
        if price_info:
            price = price_info.text.strip()
            price = re.sub('\D', '', price)

        isbn = ''
        isbn_info = soup.find('span', {'itemprop': 'isbn'})
        if isbn_info:
            isbn = isbn_info.text.strip()

        publisher = ''
        publisher_info = soup.find('span', {'itemprop': 'publisher'})
        if publisher_info:
            publisher = publisher_info.text.strip()

        cover = ''
        cover_info = soup.find('span', 'prop_name', text=re.compile(u'Переплет'))
        if cover_info:
            cover = cover_info.find_next_sibling('span').text.strip()

        pages = ''
        pages_info = soup.find('span', 'prop_name', text=re.compile(u'Страниц'))
        if pages_info:
            pages = pages_info.find_next_sibling('span').text.strip()

        year = ''
        year_info = soup.find('meta', {'itemprop': 'datePublished'})
        if year_info:
            year = year_info.get('content')[:4]

        description = ''
        description_info = soup.find('div', {'itemprop': 'description'})
        if description_info:
            description = self.remove_tags(description_info.text)

        stock = soup.find('div', 'detail-delivery__status')
        if stock:
            stock = self.remove_tags(stock.text)
        if not stock:
            stock = u"В наличии"

        images_info = soup.find('div', 'b_detail__gallery')
        if images_info:
            images_info = images_info.find('ul').find_all('li')

        pictures = []
        for img_item in images_info:
            img = img_item.find('img').get('src')
            pictures.append(img)

        row = {
            "url": url,
            "name": name
        }

        if publisher:
            row["publisher"] = publisher

        if author:
            row["author"] = author

        if description:
            row["description"] = description

        row["availability"] = stock

        if price:
            row["price"] =  {
                "currency": "RUR",
                "type": "currency",
                "content": int(price)
            }

        if year:
            row["year"] = year

        if pages:
            row["pages"] = pages

        if isbn:
            row["isbn"] = isbn

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
