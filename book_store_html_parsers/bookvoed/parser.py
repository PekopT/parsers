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
        info_content = soup.find('div', {'id': 'aboutTabs_info_content'}).table

        infos = {}
        for tr in info_content:
            td_list = tr.find_all('td')
            if u"втор" in td_list[0].text:
                infos[u"Автор"] = td_list[1].text
            else:
                infos[td_list[0].text] = td_list[1].text

        name = soup.find('h1')

        publisher = infos[u'Издательство']
        name = name.text

        author = ""
        if u"Автор" in infos:
            author = infos[u"Автор"]

        year = ""
        if u"Год" in infos:
            year = infos[u"Год"]

        pages = ""
        if u"Страниц" in infos:
            pages = infos[u"Страниц"]

        isbn = ""
        if u"ISBN" in infos:
            isbn = infos[u"ISBN"]

        cover = ""
        if u"Переплёт" in infos:
            cover = infos[u"Переплёт"]

        stock = u'В наличии'

        description = ''
        description_info = soup.find('div', {'id': 'aboutTabs_descr_content'})
        if description_info:
            description = description_info.text.strip()
            description = description.replace("\\n", "").strip()

        price = ''
        price_info = soup.find('meta', {'itemprop': 'price'})
        if price_info:
            price = price_info.get('content').split('.')[0]
            price = re.sub('\D','', price)
        else:
            stock = u'В наличии нет'


        also_buy_info = soup.select('#bookWith div div div.Kp')

        also_buy_books = []

        if also_buy_info:
            for book in also_buy_info:
                picture_book_data = book.find('img')
                picture_book = ''
                name_book = ''
                if picture_book_data:
                    picture_book = picture_book_data.get('src')
                    name_book = picture_book_data.get('title')

                author_info = book.find('bq')
                author_book = ''
                if author_info:
                    author_book = author_info.text.strip()

                url_book_info = book.a
                if url_book_info:
                    url_book = url_book_info.get('href')
                else:
                    url_book = ''

                also_row = {}

                if picture_book:
                    also_row["image"] = picture_book

                if name_book:
                    also_row["name"] = name_book

                if author_book:
                    also_row["author"] = author_book

                if url_book:
                    also_row["url"] = url_book
                if also_row:
                    also_buy_books.append(also_row)

        row = {
            "url": url,
            "name": name,
            "price": {
                "currency": u"RUR",
                "type": "currency",
                "content": int(price)
            }
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

        row["availability"] = stock

        if cover:
            row["cover"] = cover

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
                json.dumps({"url": data["url"], "traceback": traceback.format_exc()}, ensure_ascii=False).encode(
                    'utf-8') + "\n")

    parser.close_parser()


if __name__ == '__main__':
    main()
