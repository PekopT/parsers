# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from codecs import getwriter
from sys import stdout
import json

import re


class AnekdotruPipeline(object):

    def validate_str(self, value):
        if type(value) == list:
            val = None
            for v in value:
                if v.strip():
                    val = v.strip()
                    break
            if val is None:
                return u''
        else:
            val = value
        return val.strip()

    def delete_tags(self, value):
        pattern = u'\<[^>]*\>'
        value = re.sub(pattern, '', value)
        value = re.sub(u'&#13;|&lt;|&gt;|<|>|\/li|\r\n', '', value)
        value = re.sub(u'td|span|\/|br|\\\\', '', value)
        return value

    def get_date(self, value):
        date =u""
        pattern = u'\/[0-9-]+\/?$'
        m = re.search(pattern, value)
        if m:
            date = m.group(0)[1:-1]
        return date

    def process_item(self, item, spider):
        id = self.validate_str(item['id'])
        id = re.sub(u'\D','', id)
        text = ''.join(item['text'])
        text = self.delete_tags(text)

        num = self.validate_str(item['num'])
        author = item['author']
        url = item['url']
        date = self.validate_str(item['date'])
        tags = item['tags']
        rating = item['rating']
        human = {
            "id": id,
            "text": text,
            "rating":
                {
                    "positive": rating[2],
                    "negative": rating[3],
                    "num": num
                },

            "tags": tags,
            "author": author,
            "url": url,
            "date": date,
        }

        sout = getwriter("utf8")(stdout)
        sout.write(json.dumps(human, ensure_ascii=False) + "\n")
