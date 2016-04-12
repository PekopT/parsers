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

    def parse_html(self, data):
        url = data['url']
        html = data['html']
        soup = BeautifulSoup(html, 'html.parser')

        name_info = soup.title.text.strip()
        name = name_info.split('/')[0].strip()

        stock = u'В наличии'

        description_info = soup.find('meta',{'name':'Description'})
        description_data = description_info.get('content').split(';')
        for item in description_data:
            item_data = item.split(':')
            if u"Издательство" in item_data[0].strip():
                publisher = item_data[1].strip()
            else:
                publisher = ''

            if u"Автор" in item_data[0].strip():
                author = item_data[1].strip()
            else:
                author = ''

            if u"Переплет" in item_data[0].strip():
                cover = item_data[1].strip()
            else:
                cover = ''

            if u"ISBN" in item_data[0].strip():
                isbn = item_data[1].strip()
            else:
                isbn = ''

            if u"издания" in item_data[0].strip():
                year = item_data[1].strip()
                year = re.sub('\D','', year)
            else:
                year = ''

            if u"Страниц" in item_data[0].strip():
                pages = item_data[1].strip()
            else:
                pages = ''

            if u"Цена" in item_data[0].strip():
                price = item_data[1].strip()
                price = re.sub('\D','', price)
            else:
                price = ''





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

        if stock:
            row["availability"] = stock

        if cover:
            row["cover"] = cover

        if isbn:
            row["isbn"] = isbn

        if year:
            row["year"] = year

        if pages:
            row["pages"] = pages

        if publisher:
            row["publisher"] = publisher

        if author:
            row["author"] = author

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