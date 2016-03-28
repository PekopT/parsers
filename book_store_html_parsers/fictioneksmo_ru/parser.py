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

        author = soup.find('h2', {'itemprop':'author'}).text
        author = self.remove_tags(author)

        price = soup.find('span',{'itemprop':'price'})
        price = price.text.strip()



        isbn = soup.find('span', {'itemprop': 'isbn'}).text.strip()

        publisher = soup.find('span',{'itemprop': 'publisher'}).text.strip()

        cover_info = soup.find('span', 'prop_name', text=re.compile(u'Переплет'))
        cover = cover_info.find_next_sibling('span').text.strip()

        pages_info = soup.find('span', 'prop_name', text=re.compile(u'Страниц'))
        pages = pages_info.find_next_sibling('span').text.strip()

        year = soup.find('meta',{'itemprop':'datePublished'})
        year = year.get('content')[:4]

        description = soup.find('div', {'itemprop':'description'})
        description = self.remove_tags(description.text)

        stock = soup.find('div','detail-delivery__status')
        stock = self.remove_tags(stock.text)
        if not stock:
            stock = u"В наличии"

        images_info = soup.find('div','b_detail__gallery').find('ul').find_all('li')

        pictures = []
        for img_item in images_info:
            img = img_item.find('img').get('src')
            pictures.append(img)

        row = {
            "url": url,
            "name": name,
            "publisher": publisher,
            "author": author,

            "description": description,
            "price": {
                "currency": "RUR",
                "type": "currency",
                "content": int(price)
            },
            "year": year,
            "pages": pages,
            "isbn": isbn,
        }

        if stock:
            row["availability"] = stock

        if cover:
            row["cover"] = cover


        if pictures:
            row["images"] = pictures

        self.check_validate_schema(row)
        self.rows_data.append(row)


    def check_validate_schema(self, node):
        f = open('books.schema.json', 'r')
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
