# coding=utf-8
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

    def parse_html(self, data):
        url = data['url']
        html = data['html']
        soup = BeautifulSoup(html, 'html.parser')
        stock = u'В наличии'
        name = soup.find('h1').text.strip()

        description = soup.find('div', {'itemprop':'description'})
        description = description.text.strip()

        isbn_info = soup.find('span','fieldName',text=re.compile(u'ISBN')).parent.text
        isbn = isbn_info.replace(u"ISBN:","").strip()

        publisher_info = soup.find('span','fieldName',text=re.compile(u'Издательство')).parent
        cover_info = publisher_info.find_next_sibling('p')
        cover_pages = cover_info.text.split(',')
        if len(cover_pages) > 2:
            pages = cover_pages[2]
            cover = cover_pages[0] + ',' + cover_pages[1]
        elif len(cover_pages) == 2:
            pages = cover_pages[1]
            cover = cover_pages[0]
        pages = re.sub(u"\D", u"", pages)


        publisher_info = publisher_info.text.replace(u'Издательство:','')
        to_year = re.search(u'\(.+\)',publisher_info)
        if to_year:
            year_search = to_year.group(0)
            year = re.sub('\D','', year_search)

        publisher = publisher_info.replace(year_search,'').strip()

        image = soup.find('img', {"itemprop":"image"})
        image = image.get('src')
        pictures = [image]

        price_info = soup.find('span',{'itemprop':'price'})
        price = price_info.text.strip()

        author = soup.find('div', {'id':'productDescription'}).find('span', {"id":"authorsList"}).text.strip()


        also_buy_info = soup.find('div', {'id':'sectionMainOneItem'}).find_all('div',{'id':'minProductOneItem'})
        also_buy_books = []


        for book in also_buy_info:
            picture_book = book.a.find('img').get('src')
            price_info = book.find('div', 'price')
            price_book = re.sub('\D', '', price_info.text).strip()

            name_book = book.find('div', 'title').a.get_text().strip()
            url_book = book.find('div','title').a.get('href')

            also_row = {
                "url": url_book,
                "name": name_book,
                "image": picture_book,
                "price": {
                    "currency": "RUR",
                    "type": "currency",
                    "content": int(price_book),
                }
            }

            also_buy_books.append(also_row)

        row = {
            "url": url,
            "name": name,
            "publisher": publisher,
            "author": author,

            "description": description,
            "price": {
                "currency": "RUR",
                "type": "currency",
                "content": int(price)
            },
            "year": year,
            "pages": pages,
            "isbn": isbn,
        }

        if stock:
            row["availability"] = stock

        if cover:
            row["cover"] = cover

        if also_buy_books:
            row["also_buy"] = also_buy_books

        if pictures:
            row["images"] = pictures

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
