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
        name = soup.find('h1','product-name').text.strip()
        product_attribute = soup.find('ul', {'id':'product-attribute-specs-table'})

        isbn = ''
        isbn_info =product_attribute.find('span',text=re.compile(u"ISBN"))
        if isbn_info:
            isbn = isbn_info.parent.text.strip()
            isbn = isbn.replace(u"ISBN:", "").replace("\\n","").strip()

        author = ''
        author_info =product_attribute.find('span',text=re.compile(u"Автор"))
        if author_info:
            author = author_info.parent.text.strip()
            author = author.replace(u"Автор:", "").replace("\\n","").strip()

        publisher = ''
        publisher_info =product_attribute.find('span',text=re.compile(u"Издательство"))
        if publisher_info:
            publisher = publisher_info.parent.text.strip()
            publisher = publisher.replace(u"Издательство:", "").replace("\\n","").strip()

        year = ''
        year_info =product_attribute.find('span',text=re.compile(u"Год\sиздания"))
        if year_info:
            year = year_info.parent.text.strip()
            year = year.replace(u"Год издания:", "").replace("\\n","").strip()
            year = re.sub('\D', '', year)

        pages = ''
        pages_info =product_attribute.find('span',text=re.compile(u"страниц"))
        if pages_info:
            pages = pages_info.parent.text.strip()
            pages = pages.replace(u"Кол-во страниц:", "").replace("\\n","").strip()
            pages = re.sub('\D', '', pages)

        cover = ''
        cover_info =product_attribute.find('span',text=re.compile(u"Тип\sпереплета"))
        if cover_info:
            cover = cover_info.parent.text.strip()
            cover = cover.replace(u"Тип переплета:", "").replace("\\n","").strip()

        description = ''
        description_info = soup.find('div', {'id':'full_product_description'})
        if description_info:
            description = description_info.text.replace("\\n","").strip()

        price = ''
        price_info = soup.find('span','price')
        if price_info:
            price = price_info.text.strip()
            price = re.sub('\D', '', price)


        stock_info = soup.find('div','product-availability')
        if stock_info:
            stock = stock_info.text.replace("\\n","").strip()
            stock = re.sub(r'\s+', ' ', stock)
        else:
            stock = u'В наличии'

        images_info = soup.find('div',{'id':'product_gallery_etalage'})
        pictures = []
        if images_info:
            images_info = images_info.find_all('img','etalage_thumb_image')
            pictures = [img.get('src') for img in images_info]

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
