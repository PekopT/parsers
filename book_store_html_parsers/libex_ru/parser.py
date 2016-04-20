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

        images_info = soup.find_all('img', {'width':'60'})
        pictures = [img.get('src') for img in images_info]

        name = soup.h1.text.strip()

        author_info = soup.find("h3", 'nomargin')
        if author_info:
            author = author_info.text.strip()
        else:
            author = ''

        publisher_info = soup.find('td', text=re.compile(u'Издательство'))
        if publisher_info:
            publisher_info = publisher_info.text.strip()
            publisher = publisher_info.replace(u'Издательство:',"")
        else:
            publisher = ''

        isbn_info = soup.find('td', text=re.compile(u'ISBN'))
        if isbn_info:
            isbn_info = isbn_info.parent.text
            isbn = isbn_info.split(';')[0]
            isbn = isbn.replace(u'ISBN', '')
        else:
            isbn = ''

        description_info = soup.find('h3', text=re.compile(u'Аннотация'))
        if description_info:
            description = description_info.find_next_sibling('p').text.strip()
        else:
            description = ''

        price_info = soup.find('div',{'align':'right'})
        if price_info:
            price = price_info.text.strip()
            price = re.sub('\D','',price)
        else:
            price = ''


        cover_info = soup.find('a', text=re.compile(u'Переплет')).parent.text
        if cover_info:
            cover_data = cover_info.split(';')
            cover = cover_data[0]
            cover = cover.replace(u'Переплет:','').strip()
            pages = cover_data[1]
            pages = re.sub('\D', '', pages)
            year = cover_data[2]
            year = re.sub('\D', '', year)
        else:
            year = ''
            pages = ''
            cover = ''

        stock = u"В наличии"

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
