import sys
import json
import re
from codecs import getwriter
from bs4 import BeautifulSoup

sout = getwriter("utf-8")(sys.stdout)


class Parser(object):
    data = {}
    def __init__(self, url, html):
        self.url = url
        self.html = html


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

    def parse_html(self):
        soup = BeautifulSoup(self.html, 'html.parser')
        info = soup.body.div

        isbn = info.find('span', {'itemprop': 'isbn'})
        isbn = isbn.text.strip()

        author = soup.find('div', 'j-book_autors book_autors').find('span')
        author = author.text.strip()

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
        name = name.text.strip()

        pages = soup.find('td', 'pages').find('span', 'book_field')
        pages = pages.text.strip()

        publisher = soup.find('li', 'j-book_pub').find('td', 'pubhouse')
        publisher = publisher.text.strip()
        publisher = self.remove_tags(publisher)

        price_stock = soup.find('div', 'book_price3').find('div','book_price__title_ok-thin')
        price_stock = price_stock.text.strip()
        price_stock = self.remove_tags(price_stock)

        cover = soup.findAll('div', 'j-book_autors book_autors')[0].findNextSibling('ul')
        cover = cover.text.strip()
        cover = self.remove_tags(cover)

        row = {
            "url": self.url,
            "name": name,
            "author": author,
            "publisher": publisher,
            "description": description,
            "price": {
                "currency": price_currency,
                "type": "currency",
                "content": price
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

        self.data = row

    def check_validate_schema(self):
        pass

    def close_parser(self):
        sout.write(json.dumps(self.data, ensure_ascii=False))


def main():
    obj = json.load(sys.stdin)
    url = obj['url']
    html = obj['html']
    # html = open("book3.html", "rb")  for testing
    parser = Parser(url, html)
    parser.parse_html()
    parser.close_parser()

if __name__ == '__main__':
    main()
