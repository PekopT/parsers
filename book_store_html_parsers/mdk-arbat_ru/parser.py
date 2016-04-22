# coding: utf-8
import sys
import json
import re
import traceback
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

        author = ''
        author_info= soup.find('div', {'id': 'about_text'})
        if author_info:
            author_info = author_info.find('td', {'id': 'over_name_book'})
            if author_info:
                author = author_info.text.strip()

        description = ''
        description_info = soup.find_all('td', {'id': 'about_text1'})
        if description_info:
            description = description_info[1].text.strip()
        price = ''
        price_info = soup.find('table', {'id': 'price_shop'}).find_all('tr', limit=2)
        if price_info:
            price = price_info[1].find('td', 'price_book').text
            price = re.sub(u'\D', '', price)

        info_book = soup.find('div', 'opisanie')
        if info_book:
            isbn_info = info_book.find('td', text=re.compile(u'ISBN'))
            isbn = re.sub(u'ISBN:', '', isbn_info.text)

            publish_info = info_book.find('td', text=re.compile(u'Издательство'))
            publisher = re.sub(u'Издательство:', '', publish_info.text)

            pages_info = info_book.find('td', text=re.compile(u'страниц'))
            pages = pages_info.text.replace(u'Количество страниц:', u'')

        stock = u"В наличии"
        row = {}

        row["url"] = url
        row["name"] = name
        row["availability"] = stock

        if author:
            row["author"] = author

        if publisher:
            row["publisher"] = publisher

        if description:
            row["description"] = description

        if pages:
            row["pages"] = pages

        if isbn:
            row["isbn"] = isbn

        if price:
            row["price"] = {
                "currency": "RUR",
                "type": "currency",
                "content": int(price)
            }

        image_info = soup.find('div', {'id': 'image_big'}).img
        image = image_info.get('src')

        pictures = [image]

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
