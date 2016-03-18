# -*- coding: utf-8 -*-
import sys
import json
import re
from codecs import getwriter
from bs4 import BeautifulSoup

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
        name = soup.find('h1').text

        author = soup.find('div', text=re.compile(u'Автор'), attrs={'class': 'eItemProperties_name'}) \
            .find_next_sibling().find('a').text
        year = soup.find('div', text=re.compile(u'Год'), attrs={'class': 'eItemProperties_name'}) \
            .find_next_sibling().text

        pages = soup.find('div', text=re.compile(u'Количество страниц'), attrs={'class': 'eItemProperties_name'}) \
            .find_next_sibling().text

        cover = soup.find('div', text=re.compile(u'Переплет'), attrs={'class': 'eItemProperties_name'}) \
            .find_next_sibling().text

        isbn = soup.find('div', text=re.compile(u'ISBN'), attrs={'class': 'eItemProperties_name'}) \
            .find_next_sibling().text

        publisher = soup.find('div', text=re.compile(u'Издательство'), attrs={'class': 'eItemProperties_name'}) \
            .find_next_sibling().text
        description = soup.find('div', 'eProductDescriptionText_text').text
        script_text = soup.find('div', 'bContentColumn').find('script').text

        pattern = u'\"Products\"\:\[[^]]*\]'
        m = re.search(pattern, script_text)
        if m:
            also_search = m.group(0)

        also_search = also_search[11:]
        also_buy = json.loads(also_search)
        also_buy_books = []
        for book in also_buy:
            also_row = {
                "url": "http://www.ozon.ru/context/detail/id/6305434/",
                "name": book["Name"],
                "image": book["Picture"],
                "author": author,
                "price": {
                    "currency": book["PriceInfo"]["CurrencyName"],
                    "type": "currency",
                    "content": book["PriceInfo"]["PriceValue"],
                }
            }
            also_buy_books.append(also_row)

        pattern_photo = u'\"Фотографии\"\,\"Elements\"\:\[[^]]*\]'
        m_photo = re.search(pattern_photo, script_text)
        if m_photo:
            pictures_search = m_photo.group(0)[24:]

        pict_list = json.loads(pictures_search)
        pictures = []
        for p in pict_list:
            pictures.append(p['Preview'])

        price_pattern = u'\"PriceString\"\:["\d]*\,'
        m_price = re.search(price_pattern, script_text)
        if m_price:
            price = m_price.group(0)
            price = re.sub(u'\D', '', price)

        price_stock = soup.find('div', 'eOneTile_priceStock').text
        if not price_stock:
            price_stock = u"На складе."

        row = {
            "url": "http://www.ozon.ru/context/detail/id/5793186/",
            "name": name.strip(),
            "author": author.strip(),
            "publisher": publisher.strip(),
            "description": description.strip(),
            "price": {
                "currency": "RUR",
                "type": "currency",
                "content": price
            },
            "availability": price_stock,
            "year": year.strip(),
            "cover": cover.strip(),
            "pages": pages.strip(),
            "isbn": isbn.strip(),

        }
        if also_buy_books:
            row["also_buy"] = also_buy_books

        if pictures:
            row["images"] = pictures

        self.rows_data.append(row)


    def check_validate_schema(self):
        pass

    def close_parser(self):
        sout.write(json.dumps(self.rows_data, ensure_ascii=False))


def main():
    parser = Parser()
    for line in sys.stdin:
        try:
            data = json.loads(line)
            try:
                parser.parse_html(data)
            except Exception:
                print "errors parse"
        except Exception:
            print "error reading"

    parser.close_parser()


if __name__ == '__main__':
    main()
