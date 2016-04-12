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

        name = soup.h1
        name = name.text

        author_info = soup.find_all('span', 'author_link')
        authors = [auth.text for auth in author_info]
        author = ','.join(authors)

        images_info = soup.find_all('img', {'itemprop': 'image'})
        pictures = [img.get('src') for img in images_info]

        description = soup.find('span', {"itemprop": "description"}).text.strip()
        about = soup.find('span', {"itemprop": "about"})
        if about:
            description += about.text.strip()

        isbn = soup.find('p', {'itemprop': 'isbn'}).text.strip()
        pages = ''
        pages_info = soup.find('span', {'itemprop': 'numberOfPages'})

        if pages_info:
            pages = pages_info.text.strip()

        price_info = soup.find('p','newPrice')
        if price_info:
            price = price_info.text
            # print price
        # price = soup.find('span', {'itemprop': 'price'}).text.strip()
        # price = price.split('.')[0]
            price = re.sub('\D', '', price)

        cover = soup.find('link', {"itemprop": "bookFormat"})
        if cover:
            cover = self.remove_tags(cover.text.strip())

        stock = u"В наличии"
        stock_info = soup.find('link', {"itemprop": "availability"})

        if stock_info:
            stock_url = stock_info.get('href')
            if "http://schema.org/InStock" == stock_url:
                stock = u"В наличии"
            elif "http://schema.org/PreOrder" == stock_url:
                stock = u"Предзаказ. В наличии пока нет"


        # stock = self.remove_tags(stock)

        publisher_info = soup.find('span', {'itemprop': 'publisher'})

        if publisher_info:
            publisher = publisher_info.text.strip()
        else:
            publisher = ''

        year_info  = soup.find('span', {"itemprop": "datePublished"})
        if year_info:
            year = year_info.text.strip()
        else:
            year = ''

        also_buy_info = soup.find('div','weRecomBlock')
        if also_buy_info:
            also_buy_info = also_buy_info.find_all('div', 'bookWrapp')
        else:
            also_buy_info = []

        also_buy_books = []

        for book in also_buy_info:
            picture_book = book.find('img').get('src')
            price_info = book.find('p', 'bookPrice').text.strip()
            price_book = price_info.split(',')[0]
            price_book = re.sub('\D', '', price_book).strip()
            name_book = book.find('img').get('alt')
            url_book = book.a.get('href')

            also_row = {
                "url": url_book,
                "name": name_book,
                "image": picture_book,
                "price": {
                    "currency": "RUR",
                    "type": "currency",
                    "content": int(price_book),
                }
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
