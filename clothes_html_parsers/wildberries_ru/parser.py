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
        value = value.replace(u'\n', u'')
        return value

    def str_to_int(self, value):
        value = re.sub(u'\D', u'', value)
        return value

    def get_images(self, soup):
        images = []

        return images

    def parse_html(self, data):
        url = data['url']
        html = data['html']
        soup = BeautifulSoup(html, 'html.parser')
        name = soup.h1.text.strip()

        head = soup.find('div', 'pager').find('span', 'total many').strong
        item_count = head.text
        item_count = re.sub('\D', '', item_count)

        item_list = []
        products_catalog = soup.find('div', 'catalog_main_table')
        products = products_catalog.find_all('div', 'dtList')

        for prod in products:
            brand = prod.a.find('strong', 'brand-name').text.strip()
            title = prod.a.find('span', 'goods-name').text.strip()
            url_item = prod.a.get('href')
            image = prod.find('img').get('data-original')
            price = prod.find('span', 'price')

            price = re.sub('\D', '', price.text).strip()
            row_item = {
                "image": image,
                "url": url_item,
                "brand": brand,
                "name": title,
                "price": {
                    "currency": "RUR",
                    "type": "currency",
                    "content": int(price)
                }
            }
            item_list.append(row_item)

        row = {}
        url = url.replace("https", "http")  # todo
        row[url] = {}
        row[url]["url"] = url
        row[url]["list_name"] = name
        row[url]["item_count"] = int(item_count)

        if item_list:
            row[url]["item_list"] = item_list


        self.check_validate_schema(row)
        self.rows_data.append(row)

    def check_validate_schema(self, node):
        f = open('clothes.schema.json', 'r')
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
