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

        name = soup.find('h1').text.replace("\\n","").strip()

        year_info = soup.find('span', {'id':'ctl03_lblYear'})
        if year_info:
            year = year_info.text.strip()
            year = re.sub('\D','', year)

        isbn = ''
        isbn_info = soup.find('span', {'id':'ctl03_lblIsbn'})
        if isbn_info:
            isbn = isbn_info.text.strip()
            isbn = isbn.replace(u"ISBN:","").strip()

        pages = ''
        cover = ''
        pages_info = soup.find('span', {'id':'ctl03_lblCoverTypeNPages'})
        if pages_info:
            pages_text = pages_info.text.strip()
            pages_data = pages_text.split(',')
            if len(pages_data) == 2:
                pages = pages_data[1]
                pages = re.sub('\D', '', pages)
                cover = pages_data[0].strip()

        publisher = ''
        publisher_info = soup.find('a', {'id':'ctl03_lbtPublisher'})
        if publisher_info:
            publisher = publisher_info.text.strip()

        price = ''
        price_info = soup.find('span',{'id': 'ctl03_lblPrice'})
        if price_info:
            price = price_info.text.strip()
            price = re.sub('\D', '', price)

        description_info = soup.find('span', {'id': 'ctl03_lblDescription'})
        if description_info:
            description = description_info.text.strip()


        pictures = []
        images_info = soup.find('img', {'id':'ctl03_imgPhoto'})
        if images_info:
            image_src = images_info.get('src')
            pictures.append(image_src)

        author = ''
        author_info = soup.find('', {'id':'ctl03_lbtAuthor'})
        if author_info:
            author = author_info.text.strip()

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

        row["availability"] = u"В наличии"

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
