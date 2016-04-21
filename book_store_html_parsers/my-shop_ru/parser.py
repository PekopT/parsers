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
        name = soup.h1.text.strip()

        stock = u"В наличии"
        row = {}
        row["url"] = url
        row["name"] = name

        author = ''
        author_info = soup.find('td',text=re.compile(u"автор\/составитель"))
        if author_info:
            author = author_info.previous_sibling.text.strip()

        description = ''
        pictures = []
        description_info = soup.find('td', {'data-o': 'good_description'})
        if description_info:
            description_info = description_info.select("table tr")[2]
            if description_info:
                images_info = description_info.find_all('img')
                if images_info:
                    pictures = [img.get('src') for img in images_info]
                description = description_info.text.strip()

        div_small = soup.find('div', )

        year = ''
        year_info = soup.find('', text=re.compile(ur'дата\sвыпуска', re.DOTALL))
        if year_info:
            year = year_info
            year = re.sub('\D', '', year)

        isbn = ''
        isbn_info = soup.find('span', text=re.compile(u"ISBN"))
        if isbn_info:
            isbn = isbn_info.text.strip()
            isbn = isbn.replace(u"ISBN:","").strip()


        cover = ''
        cover_info = soup.find('', text=re.compile(u"переплет"))
        if cover_info:
            cover = cover_info.strip()

        publisher = ''
        publisher_info = soup.find('',text=re.compile(u"Издательство"))
        if publisher_info:
            publisher = publisher_info.next_sibling.text.strip()

        pages = ''
        pages_info = soup.find('',text=re.compile(u"количество\sстраниц"))
        if pages_info:
            pages = pages_info.strip()
            pages = re.sub('\D','', pages)


        price = ''
        price_info = soup.find('td','bgcolor_2 list_border')
        if price_info:
            price_info = price_info.find('b')
            if price_info:
                price = price_info.text.strip()
                price = re.sub('\D', '', price)

        # price_info = soup.find('td', 'w184 vat').find('table','w100p').find('b', {'style':'font-size:14px'})
        # price = re.sub(u'\D',u'', price_info.text)


        also_buy_info = soup.find('table',{'data-o':'showcase_complementary'})
        if also_buy_info:
            also_buy_info_td = also_buy_info.find_all('tr')[1].find_all('td')
        else:
            also_buy_info_td = []


        also_buy_books = []

        for book in also_buy_info_td:
            picture_book = book.find('img').get('src')
            name_book = book.find('span', 'small1').text.strip()
            price_book = book.find('div','small1').text.strip()
            price_book = re.sub('\D','', price_book)
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
                json.dumps({"url": data["url"], "traceback": traceback.format_exc()}, ensure_ascii=False).decode('windows-1251').encode(
                    "utf-8") + "\n")

    parser.close_parser()


if __name__ == '__main__':
    main()
