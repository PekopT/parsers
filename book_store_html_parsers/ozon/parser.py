# -*- coding: utf-8 -*-
import sys
import json
import re
from codecs import getwriter
from bs4 import BeautifulSoup

sout = getwriter("utf-8")(sys.stdout)

def remove_tags(value):
    # value = re.sub('')
    return value

def parse_data(data):
    soup = BeautifulSoup(data, 'html.parser')
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
    script_text  = soup.find('div', 'bContentColumn').find('script').text

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
                "name":book["Name"] ,
                "image": book["Picture"],
                "author": u"Айн Рэнд",
                "price": {
                    "currency": book["PriceInfo"]["CurrencyName"],
                    "type": "currency",
                    "content": book["PriceInfo"]["PriceValue"],
                }
        }
        also_buy_books.append(also_row)

    row = {
        "url": "http://www.ozon.ru/context/detail/id/5793186/",
        "name": name.strip(),
        "images": [
            "http://static2.ozone.ru/multimedia/books_covers/c300/1005820676.jpg",
            "http://static2.ozone.ru/multimedia/books_covers/c300/1005820676-2.jpg",
        ],
        "author": author.strip(),
        "publisher": publisher.strip(),
        "description": description.strip(),
        "price": {
            "currency": "RUR",
            "type": "currency",
            "content": 403
        },
        "availability": u"На складе.",
        "year": year.strip(),
        "cover": cover.strip(),
        "pages": pages.strip(),
        "isbn": isbn.strip(),

    }

    if also_buy_books:
        row["also_buy"] = also_buy_books

    sout.write(json.dumps(row, ensure_ascii=False))


def main():
    data = ''
    for line in sys.stdin:
        line = line.decode('windows-1251')
        data += line
    parse_data(data)


if __name__ == "__main__":
    main()
