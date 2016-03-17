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
        publisher = soup.find('div', 'publisher').text
        publisher = publisher.replace(u'Издательство:','')
        publishers = publisher.split(',')
        publisher = publishers[0]
        year = publishers[1]
        cover = ''
        stock = ''
        isbn = soup.find('div', 'isbn').text
        price = soup.find('span', 'buying-price-val-number')
        price_currency = soup.find('span', 'buying-pricenew-val-currency').text

        if not price:
            price = soup.find('span', 'buying-pricenew-val-number')

        price = price.text

        description = soup.find('div', {'id': 'product-about'})
        description = description.text

        pages = soup.find('div', 'pages2')
        pages = pages.text

        author = soup.find('div', 'authors').find('a')
        author = author.text

        row = {
            "url": url,
            "name": name,
            "author": author,
            "publisher": publisher,
            "description": description,
            "price": {
                "currency": price_currency,
                "type": "currency",
                "content": price
            },
            "availability": stock,
            "year": year,
            "cover": cover,
            "pages": pages,
            "isbn": isbn,
        }

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
                pass
        except Exception:
            pass

    parser.close_parser()

if __name__ == '__main__':
    main()
