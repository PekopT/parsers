import sys
import json
import re
from codecs import getwriter
from bs4 import BeautifulSoup

sout = getwriter("utf-8")(sys.stdout)


class BaseParser(object):
    rows_data = []

    def remove_tags(self, value):
        value = value.replace(u'\n', u'')
        return value

    def str_to_int(self, value):
        value = re.sub(u'\D', u'', value)
        return value

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
        name = soup.h1.text.strip()

        stock = u"В наличии"
        row = {}
        row["url"] = url
        row["name"] = name
        row["availability"] = stock

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
