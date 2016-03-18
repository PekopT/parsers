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
        image_ul = soup.find('ul', 'book_image__slidebar_itemlist j-slidebar-product-previews__list').findAll('li')

        for li in image_ul:
            img_src = li.find('img')
            images.append(img_src.get('src'))

        return images

    def parse_html(self, data):
        url = data['url']
        html = data['html']
        soup = BeautifulSoup(html, 'html.parser')

        name = soup.h1.text.strip()

        description = soup.find('span', {'itemprop': 'description'})
        description = description.text.strip()

        price_info = soup.find('div', {'id':'sTxt'}).find('div', 'price').span.span
        price = price_info.text.strip()
        price = re.sub('\D', '', price)

        book_info = soup.find('div', {'id':'fTxt'})

        isbn_info = book_info.find('span', {'itemprop':'isbn'})
        isbn = isbn_info.text.strip()

        publisher_info = book_info.find('span', {'itemprop':'publisher'})
        publisher = publisher_info.text.strip()

        pages = book_info.find('span', {'itemprop':'numberOfPages'})
        pages = pages.text.strip()

        publisher = publisher.replace(u"Издательство:",u'').strip()
        isbn = isbn.replace(u"ISBN:",u"").strip()

        year = book_info.find('p',text=re.compile(u"Год")).text
        year = re.sub('\D', '', year)

        cover = book_info.find('p',text=re.compile(u"обложки")).text
        cover = cover.replace(u"Тип обложки:","").strip()

        author = soup.find('span', {'itemprop':'creator'})
        author = author.text.strip()

        image = soup.find('img',{'id':'DETAIL_PICTURE_1'}).get('src')
        pictures = [image]

        stock = soup.find('div', 'stock-msg')
        qs_msg = stock.span.text
        stock = stock.text.replace(qs_msg,'').strip()


        row = {}
        row["url"] = url
        row["name"] = name
        row["availability"] = stock
        row["author"] = author
        row["publisher"] = publisher
        row["description"] = description
        row["price"] = {
                    "currency": "RUR",
                    "type": "currency",
                    "content": int(price)
        }

        row["year"] = year
        row["cover"] = cover
        row["pages"] = pages
        row["isbn"] = isbn

        also_buy_info = soup.find_all('div', 'b-carousel-block')
        also_buy_books = []
        for book in also_buy_info:
            name = book.find('div', 'zNameBox').text
            author = book.find('div', 'AutorBox').text
            url = book.a.get('href')
            image = book.img.get('src')
            price_info = book.find('div', 'boxPriceItem2').span
            price = price_info.text
            price = re.sub(u'\D', u'', price)

            also_row = {
                "url": url,
                "name": name,
                "image": image,
                "author": author,
                "price": {
                    "currency": "RUR",
                    "type": "currency",
                    "content": int(price),
                }
            }
            also_buy_books.append(also_row)

        if pictures:
            row["images"] = pictures

        if also_buy_books:
            row["also_buy"] = also_buy_books

        try:
            self.check_validate_schema(row)
            self.rows_data.append(row)
        except Exception as e:
            print e.message

        # self.rows_data.append(row)

    def check_validate_schema(self, node):
        f = open('books.schema.json', 'r')
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
