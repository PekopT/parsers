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
        name = soup.find('div',{'id':'product-list-headline'}).h1.text.strip()
        head = soup.find('div',{'id':'product-list-headline'})
        item_count = head.find('p','product-list-headline-product-count')
        item_count = re.sub(u'\D',u'',item_count.text)

        item_list = []
        products = soup.find_all('div', 'product-list-item')

        for prod in products:
            price = prod.find('span','product-price').find('span','price')
            brand = prod.find('span', 'product-brand').text.strip()
            title = prod.find('span', 'product-title').text.strip()
            image = prod.find('span', 'product-image').find('noscript').find('img').get('src')
            url_item = prod.find('a','product-link').get('href')

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

