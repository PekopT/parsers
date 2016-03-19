# coding: utf-8
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

        author = soup.find('div', {'id': 'about_text'}).find('td', {'id': 'over_name_book'})
        author = author.text.strip()

        description = soup.find_all('td', {'id': 'about_text1'})
        description = description[1].text.strip()

        price_info = soup.find('table', {'id': 'price_shop'}).find_all('tr', limit=2)
        price = price_info[1].find('td', 'price_book').text
        price = re.sub(u'\D','', price)

        info_book = soup.find('div', 'opisanie')
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
        row["author"] = author
        row["publisher"] = publisher
        row["description"] = description
        row["pages"] = pages
        row["isbn"] = isbn

        row["price"] = {
            "currency": "RUR",
            "type": "currency",
            "content": int(price)
        }

        image_info = soup.find('div',{'id':'image_big'}).img
        image = image_info.get('src')

        pictures = [image]

        if pictures:
            row["images"] = pictures

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

