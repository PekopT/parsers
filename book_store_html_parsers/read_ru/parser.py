# -*- coding: utf-8 -*-
import sys
import json
import traceback
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
        image_ul = soup.find('ul', 'book_image__slidebar_itemlist j-slidebar-product-previews__list')
        if image_ul:
            image_ul = image_ul.findAll('li')

        if image_ul:
            for li in image_ul:
                img_src = li.find('img')
                images.append(img_src.get('src'))

        return images

    def parse_html(self, data):
        url = data['url']
        html = data['html']
        soup = BeautifulSoup(html, 'html.parser')

        info = soup.body.div

        isbn_info = info.find('span', {'itemprop': 'isbn'})
        if isbn_info:
            isbn = isbn_info.text.strip()
        else:
            isbn = ''

        isbn = isbn.replace('\\n', '')

        author_info = soup.find('div', 'j-book_autors book_autors')
        if author_info:
            author = author_info.find('span')
            author = author.text.replace('\\n', '').strip()
        else:
            author = ''

        price_info = soup.find('div', 'book_price3__fullprice')

        if price_info:
            price = price_info.find('div', {'itemprop': 'price'})
            price = price.text.strip()
            price = self.str_to_int(price)
        else:
            price = ''

        year = info.find('meta', {'itemprop': 'datePublished'})

        if year:
            year = year.get('content').strip()
        else:
            year = ''

        description = info.find('span', {'itemprop': 'description'})
        if description:
            description = description.text.strip()
            description = self.remove_tags(description)
        else:
            description = ''

        name = info.find('span', {'itemprop': 'name'})
        if name:
            name = name.text.replace('\\n', '').strip()
        else:
            name = ''

        pages_td = soup.find('td', 'pages')

        if pages_td:
            pages = pages_td.find('span', 'book_field')
            if pages:
                pages = pages.text.replace('\\n', '').strip()
            else:
                pages = ''
        else:
            pages = ''

        publisher_info = soup.find('li', 'j-book_pub')
        if publisher_info:
            publisher = publisher_info.find('td', 'pubhouse')
            publisher = publisher.text.strip()
            publisher = self.remove_tags(publisher)
            publisher = publisher.replace('\\n', '').strip()

        price_stock_info = soup.find('div', 'book_price3')
        if price_stock_info:
            price_stock = price_stock_info.find('div', 'book_price__title_ok-thin')
            if price_stock:
                price_stock = price_stock.text.replace('\\n', '').strip()
                price_stock = self.remove_tags(price_stock)
            else:
                price_stock = u'В наличии'
        else:
            price_stock = u'В наличии'

        cover_info = soup.findAll('div', 'j-book_autors book_autors')
        if cover_info:
            cover_ul = cover_info[0].findNextSibling('ul')
            if cover_ul:
                cover = cover_ul.text.replace('\\n', '').strip()
                cover = self.remove_tags(cover)
            else:
                cover = ''
        else:
            cover = ''

        row = {}

        row["url"] = url
        row["name"] = name

        row["availability"] = price_stock

        if price:
            row["price"] = {
                "currency": "RUR",
                "type": "currency",
                "content": int(price)
            }

        if author:
            row["author"] = author

        if description:
            row["description"] = description

        if publisher:
            row["publisher"] = publisher

        if year:
            row["year"] = year

        if pages:
            row["pages"] = pages

        if isbn:
            row["isbn"] = isbn

        if cover:
            row["cover"] = cover

        images = self.get_images(soup)
        if images:
            row["images"] = images

        self.check_validate_schema(row)
        sout.write(json.dumps(row, ensure_ascii=False) + "\n")

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
