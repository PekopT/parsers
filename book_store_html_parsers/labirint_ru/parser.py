# coding=utf-8
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

    def parse_html(self, data):
        url = data['url']
        html = data['html']
        soup = BeautifulSoup(html, 'html.parser')
        name = soup.find('h1').text
        publisher = soup.find('div', 'publisher').text
        publisher = publisher.replace(u'Издательство:', '')
        publishers = publisher.split(',')
        publisher = publishers[0]
        year = publishers[1]
        cover = ''
        stock = ''
        isbn = soup.find('div', 'isbn').text
        isbn = isbn.replace(u"ISBN:", u"")

        price = soup.find('span', 'buying-price-val-number')
        price_currency = soup.find('span', 'buying-pricenew-val-currency').text

        if not price:
            price = soup.find('span', 'buying-pricenew-val-number')

        price = price.text

        description = soup.find('div', {'id': 'product-about'})
        description = description.text

        pages = soup.find('div', 'pages2')
        pages = pages.text.strip()

        pages = re.sub(u'\D', u'', pages)
        year = re.sub(u'\D', u'', year)

        author = soup.find('div', 'authors').find('a')
        author = author.text

        if u"руб" in price_currency:
            price_currency = u"RUR"

        stock = soup.find('div', 'prodtitle-availibility').span.text.strip()

        row = {
            "url": url,
            "name": name,
            "price": {
                "currency": price_currency,
                "type": "currency",
                "content": int(price)
            },
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
