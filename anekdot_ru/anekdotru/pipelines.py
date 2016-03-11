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
        text = self.validate_str(item['text'])
        num = self.validate_str(item['num'])
        author = item['author']
        url = item['url']
        date = self.validate_str(item['date'])
        tags = item['tags']

        human = {
            "id": id,
            "text": text,
            "rating":
                {
                    "positive": u"",
                    "negative": u"",
                    "num": num
                },

            "tags": tags,
            "author": author,
            "url": url,
            "date": date,
        }

        sout = getwriter("utf8")(stdout)
        sout.write(json.dumps(human, ensure_ascii=False) + "\n")
