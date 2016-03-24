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

        m = re.search("\(.+\)", name)

        if m:
            search_sub = m.group(0)
            name = name.replace(search_sub,'').strip()
            item_count = re.sub('\D','',search_sub)

        item_list = []
        products = soup.find('ol','productsBox').find_all('li')

        for prod in products:
            product_data = prod.find('div', 'productDataBox')
            brand = product_data.find('span', 'productBrand')
            if brand:
                brand = brand.text.strip()
            product_headline = product_data.find('span', 'productHeadline')
            title = product_headline.a.text.strip()
            url_item = product_headline.a.get('href')

            price_info = prod.find('div', 'productPrice')
            price = re.sub('\D','',price_info.text)

            image_info = prod.find('div', 'productImageBox').img
            image = image_info.get('data-original')

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

            if brand:
                row_item["brand"] = brand
            item_list.append(row_item)

        row = {}
        row[url] = {}
        row[url]["url"] = url
        row[url]["list_name"] = name
        if item_count:
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
