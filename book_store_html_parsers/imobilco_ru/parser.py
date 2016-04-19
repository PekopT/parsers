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

        name_info = soup.h1
        name = name_info.text.strip()
        rating = name_info.find('span','rating')
        if rating:
            name = name.replace(rating.text,'')

        author = soup.find('h2', 'product-author').text.strip()

        publisher_info = soup.find('p','product-publisher').text.strip()
        publisher_data = publisher_info.split(',')
        year = publisher_data[len(publisher_data)-1].strip()
        year = re.sub('\D','',year)
        publisher = ''.join(publisher_data[:len(publisher_data)-1])

        description = soup.find('div',{'itemprop':'description'}).text.strip()
        description = description.replace('\\n','').strip()

        images_info = soup.find('span','product-image book')
        if images_info:
            images = images_info.find_all('img')
            pictures = [img.get('src') for img in images]
        else:
            pictures = []

        also_buy_info = soup.find('ul', 'product-list-similar')

        if also_buy_info:
            also_buy_info = also_buy_info.find_all('li')
        else:
            also_buy_info = []


        also_buy_books = []


        price = ''
        price_info = soup.find('span','product-price-in-button')
        if price_info:
            price_info = price_info.find('span','money-value')
            price = price_info.text.strip()
            price = re.sub('\D','',price)


        stock = u'В наличии'

        stock_info = soup.find('span', 'product-action-buy-unavailable')
        if stock_info:
            stock = stock_info.text.strip()


        for book in also_buy_info:
            picture_book = book.a.find('img').get('src')
            name_book = book.find('span', 'product-list-title-label').text.strip()
            author_book = book.find('h4', 'product-list-author').text.strip()
            author_book = author_book.split(',')[0].strip()
            url_book = book.a.get('href')

            also_row = {
                "url": url_book,
                "name": name_book,
                "image": picture_book,
                "author": author_book,
            }

            also_buy_books.append(also_row)


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

        if description:
            row["description"] = description

        if author:
            row["author"] = author

        if publisher:
            row["publisher"] = publisher

        if stock:
            row["availability"] = stock

        if year:
            row["year"] = year

        if also_buy_books:
            row["also_buy"] = also_buy_books

        if pictures:
            row["images"] = pictures


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
