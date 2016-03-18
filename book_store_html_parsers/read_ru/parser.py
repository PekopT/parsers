import sys
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

        info = soup.body.div

        isbn = info.find('span', {'itemprop': 'isbn'})
        isbn = isbn.text.strip()

        isbn = isbn.replace('\\n','')

        author = soup.find('div', 'j-book_autors book_autors').find('span')
        author = author.text.replace('\\n', '').strip()

        price = soup.find('div', 'book_price3__fullprice').find('div', {'itemprop': 'price'})
        price = price.text.strip()
        price = self.str_to_int(price)

        price_currency = info.find('meta', {'itemprop': 'priceCurrency'})
        price_currency = price_currency.get('content').strip()

        year = info.find('meta', {'itemprop': 'datePublished'})
        year = year.get('content').strip()

        description = info.find('span', {'itemprop': 'description'})
        description = description.text.strip()
        description = self.remove_tags(description)

        name = info.find('span', {'itemprop': 'name'})
        name = name.text.replace('\\n', '').strip()

        pages = soup.find('td', 'pages').find('span', 'book_field')
        pages = pages.text.replace('\\n', '').strip()

        publisher = soup.find('li', 'j-book_pub').find('td', 'pubhouse')
        publisher = publisher.text.strip()
        publisher = self.remove_tags(publisher)
        publisher = publisher.replace('\\n', '').strip()

        price_stock = soup.find('div', 'book_price3').find('div','book_price__title_ok-thin')
        price_stock = price_stock.text.replace('\\n', '').strip()
        price_stock = self.remove_tags(price_stock)

        cover = soup.findAll('div', 'j-book_autors book_autors')[0].findNextSibling('ul')
        cover = cover.text.replace('\\n', '').strip()
        cover = self.remove_tags(cover)

        row = {
            "url": url,
            "name": name,
            "author": author,
            "publisher": publisher,
            "description": description,
            "price": {
                "currency": price_currency,
                "type": "currency",
                "content": int(price)
            },
            "availability": price_stock,
            "year": year,
            "cover": cover,
            "pages": pages,
            "isbn": isbn,
        }

        images = self.get_images(soup)
        if images:
            row["images"] = images

        try:
            self.check_validate_schema(row)
            self.rows_data.append(row)
        except Exception as e:
            print e.message

        # self.rows_data.append(row)

    def check_validate_schema(self, node):
        f = open('books.schema.json', 'r')
        schema = json.loads(f.read())
        validate(node, schema)

    def close_parser(self):
        sout.write(json.dumps(self.rows_data, ensure_ascii=False))


def main():
    parser = Parser()
    for line in sys.stdin:
        try:
            data = json.loads(line)
            try:
                parser.parse_html(data)
            except Exception as e:
                print str(e)
        except Exception as e:
                print str(e)

    parser.close_parser()


if __name__ == '__main__':
    main()

