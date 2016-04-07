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
        image_ul = soup.find('ul', 'book_image__slidebar_itemlist j-slidebar-product-previews__list').findAll('li')

        for li in image_ul:
            img_src = li.find('img')
            images.append(img_src.get('src'))

        return images

    def parse_html(self, data):
        url = data['url']
        html = data['html']
        soup = BeautifulSoup(html, 'html.parser')
        author = soup.h1.text.strip()

        name = soup.find('div','binfo').div.b
        name = name.text.strip()

        book_info = soup.find('td', 'ann')

        details = book_info.find('div','db')

        publisher_info = details.find('span',{'itemprop':'brand'})
        if publisher_info:
            publisher = publisher_info.text.replace('\\n','').strip()

        stock_info = soup.find('div','binfo').find('span','cOrange')
        stock = stock_info.text

        desc_info = soup.find('div', {'itemprop':'descr'})
        description = desc_info.text.replace('\\n','').strip()

        row = {}
        row["url"] = url
        row["name"] = name
        row["availability"] = stock
        row["author"] = author
        row["publisher"] = publisher
        row["description"] = description
        price_info = soup.find('div', 'Pic').div
        if price_info:
            price = price_info.text.strip()
            price = re.sub('\D', '', price)
            row["price"] = {
                    "currency": "RUR",
                    "type": "currency",
                    "content": int(price)
            }

        also_buy_info = soup.find_all('div', {'itemprop': "itemListElement"})

        also_buy_books = []
        for book in also_buy_info:
            name = book.h2.text.strip()
            author = book.find('div', 'p4').b.text.strip()
            url = book.h2.a.get('href')
            image = book.find('img')
            image = image.get('src')
            price_info = book.find('div', 'Pic').div
            price = price_info.text
            price_book = re.sub(u'\D', u'', price)
            also_row = {
                "url": url,
                "name": name,
                "image": image,
                "author": author,
                "price": {
                    "currency": "RUR",
                    "type": "currency",
                    "content": int(price_book),
                }
            }
            also_buy_books.append(also_row)

        if also_buy_books:
            row["also_buy"] = also_buy_books


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

