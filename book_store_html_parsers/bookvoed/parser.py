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
        info_content = soup.find('div', {'id':'aboutTabs_info_content'}).table

        infos = {}
        for tr in info_content:
            td_list = tr.find_all('td')
            infos[td_list[0].text] = td_list[1].text

        name = soup.find('h1')

        name = str(name)
        author = infos[u'Автор']
        publisher = infos[u'Издательство']
        year = infos[u'Год']
        pages = infos[u'Страниц']
        isbn = infos[u"ISBN"]
        cover = infos[u"Переплёт"]

        stock = u''

        description_info= soup.find('div', {'id':'aboutTabs_descr_content'})
        description = description_info.text

        price = soup.find('meta', {'itemprop': 'price'})
        price_currency = soup.find('meta', {'itemprop': 'priceCurrency'})
        price = price.get('content')
        price_currency = price_currency.get('content')
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
