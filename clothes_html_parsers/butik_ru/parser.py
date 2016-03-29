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

        item_count = 10

        item_list = []
        products = soup.select('li div.main-data')

        for prod in products:
            attr_products = prod.find('div', 'attrProducts')
            brand = attr_products.find('p', 'manufacter').text.strip()
            title = attr_products.find('div','pr_name_wrap').find('p','pr_name').text.strip()
            image = prod.find('img').get('data-original')
            url_item = prod.find('a').get('href')
            price_info = attr_products.find('p', 'prices').find('span', 'new-price')
            if not price_info:
                price_info = attr_products.find('p','prices').find('span','price')

            price = re.sub('\D', '', price_info.text).strip()
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