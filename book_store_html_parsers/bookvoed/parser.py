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
        # html = open('book1.html','rb')

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
        author = infos[u'Автор']

        year = infos[u'Год']
        pages = infos[u'Страниц']
        isbn = infos[u"ISBN"]
        cover = infos[u"Переплёт"]

        stock = u'В наличии'

        description_info = soup.find('div', {'id': 'aboutTabs_descr_content'})
        description = description_info.text.strip()
        description = description.replace("\\n", "").strip()

        price = soup.find('meta', {'itemprop': 'price'})
        price_currency = soup.find('meta', {'itemprop': 'priceCurrency'})
        price = price.get('content').split('.')[0]

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

        if stock:
            row["availability"] = stock

        if cover:
            row["cover"] = cover

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
