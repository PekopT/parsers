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

    def get_images(self, soup):
        images = []

        return images

    def parse_html(self, data):
        url = data['url']
        html = data['html']
        soup = BeautifulSoup(html, 'html.parser')
        name = soup.h1.text.strip()

        head = soup.find('span', {'id':'BCrArticlesTotal'})
        item_count = re.sub('\D', '', head.text)

        item_list = []
        products = soup.find_all('div', 'nmProduct')

        for prod in products:
            title = prod.find('div', 'artH1').text.strip()
            brand = prod.find('div', 'brandName').text.strip()
            price = prod.find('div', 'priceInfo').find('div', 'price')
            url_item = prod.find('a', 'brandProductLink').get('href')
            image = prod.find('span', 'sliderItem').find('img').get('src')
            price_data = price.text.strip().split('.')
            price = price_data[0]

            price = re.sub('\D', '', price).strip()
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

        try:
            self.check_validate_schema(row)
            self.rows_data.append(row)
        except Exception as e:
            print e.message

    def check_validate_schema(self, node):
        f = open('clothes.schema.json', 'r')
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
