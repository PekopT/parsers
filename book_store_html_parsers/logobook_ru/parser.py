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


        name = soup.h1.text

        author_info = soup.find_all(text=re.compile(u'Автор\:'))
        if author_info:
            author = author_info[0].next_sibling.text.strip()
        else:
            author = ''


        isbn_info = soup.find_all('font', text=re.compile(u'ISBN'))
        parent_data = isbn_info[1].parent

        description = parent_data.find(text=re.compile(u'Описание'))
        if description:
            description = description.strip()
            description = description.replace(u'Описание:','').strip()
        else:
            description = ''

        cover_info = soup.find('font', text=re.compile(u'Обложка'))
        if cover_info:
            cover_data=cover_info.text.split(':')
            if len(cover_data)>1:
                cover = cover_data[1]
            else:
                cover = cover_info.text
        else:
            cover = ''


        isbn_data = parent_data.find_all('font', text=re.compile(u'ISBN'))
        isbn_str = u''
        for isbn_t in isbn_data:
            isbn_str += isbn_t.text.split(':')[1] + ','

        isbn = isbn_str[:-1].strip()

        pages = ''
        pages_info = soup.find('font', text=re.compile(u'Страницы'))
        if pages_info:
            pages = pages_info.text
            pages = re.sub('\D','',pages)


        publisher_info = soup.find('font', text=re.compile(u'Издательство'))
        publisher = publisher_info.find_next_sibling('a')
        if not publisher:
            publisher = publisher_info.find_next_sibling('font')

        if publisher:
            publisher = publisher.text.strip()

        year_info = soup.find('font', text=re.compile(u'издания'))

        year = u''
        if year_info:
            year_data = year_info.text.split(':')
            if len(year_data)>1:
                year = year_data[1]


        images = soup.select('tr[valign=Top] td[align=center] div img')
        pictures = [images[0].get('src')]

        price = ''
        price_info = soup.find('font',{"style":"font-size: 10pt"})
        if price_info:
            price = price_info.text.split('.')[0]
            price = price.strip()


        stock = u"В наличии"

        also_buy_books = []
        also_books = soup.find_all('p',{'style':'text-align: left ;padding-left: 10px '})
        for book in also_books:
            price_book = book.find('font', text=re.compile(u'Цена'))
            if price_book:
                m = re.search(u'от.?\d+', price_book.text)
                if m:
                    price_book = m.group(0)
                else:
                    price_book = price_book.text
            price_book = re.sub('\D','',price_book)
            name_book = book.find(text=re.compile(u'Название'))
            name_book = name_book.parent.b.text
            picture_book =  book.parent.find_previous_sibling('td').find('img').get('src')
            url_book = book.parent.find_previous_sibling('td').find('a').get('href')

            also_row = {}
            if price_book:
                also_row["price"] = {
                    "currency": "RUR",
                    "type": "currency",
                    "content": int(price_book),
                }
            also_row["url"] = url_book
            also_row["name"] = name_book
            also_row["image"] = picture_book

            also_buy_books.append(also_row)

        row = {
            "url": url,
            "name": name,

        }

        if price:
            row["price"] = {
                "currency": "RUR",
                "type": "currency",
                "content": int(price)
            }

        if publisher:
            row["publisher"] = publisher

        if pages:
            row["pages"] = pages

        if isbn:
            row["isbn"] = isbn

        if stock:
            row["availability"] = stock

        if description:
            row["description"] = description

        if author:
            row["author"] = author

        if year:
            row["year"] = year

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
