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
        head = soup.find('div','heading').h2
        name = head.text.strip()

        item_info = soup.find('span', 'filterinfo')
        item_count = item_info.find('span', 'total-count').text.strip()

        item_list = []
        products_info = soup.find('div','product-items-wrapper')
        products = products_info.find_all('div','col-3')

        for prod in products:
            headline = prod.find('h3', 'product-item-headline')
            url_item = headline.a.get('href')
            title = headline.text.strip()
            image_info = prod.find('div','product-item-image-wrapper').img
            image = image_info.get('src')
            price_info = prod.find('div','product-item-price')
            price = price_info.text.strip()
            price = re.sub('\D', '', price).strip()
            row_item = {
                "image": image,
                "url": url_item,
                "name": title,
                "price": {
                    "currency": "RUR",
                    "type": "currency",
                    "content": int(price)
                }
            }
            item_list.append(row_item)

        products_large = products_info.find_all('div','col-6')

        for prod in products_large:
            headline = prod.find('h3', 'product-item-headline')
            url_item = headline.a.get('href')
            title = headline.text.strip()
            image_info = prod.find('div','product-item-image-wrapper').img
            image = image_info.get('src')
            price_info = prod.find('div','product-item-price')
            price = price_info.text.strip()
            price = re.sub('\D', '', price).strip()
            row_item = {
                "image": image,
                "url": url_item,
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
