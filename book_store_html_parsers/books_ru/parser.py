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

        name = soup.h1
        name = name.text.strip()

        isbn_li = soup.find('ul', 'isbn-list').find('li', 'first')
        isbn = isbn_li.find('span')
        isbn = isbn.text.strip()

        pages_info = isbn_li.findNextSibling('li')
        pages = pages_info.text.strip()

        year = pages_info.findNextSibling('li')
        year = year.text.strip()

        author = soup.find('p', 'author')
        author = author.text

        price_info = soup.find('div','yprice price')
        price = price_info.text

        price = self.str_to_int(price)

        description_info = soup.find('div', 'note')
        description = description_info.text.strip()

        price_currency = "RUR"
        stock = u'На складе'
        cover_info = soup.find('td',text=re.compile(u'Обложка')).findNextSibling('td')
        cover = cover_info.text.strip()

        publisher_info = soup.find('td',text=re.compile(u'Издательство')).findNextSibling('td')
        publisher = publisher_info.text.strip()

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
