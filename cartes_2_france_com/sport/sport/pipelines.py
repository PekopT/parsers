# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from codecs import getwriter
from sys import stdout
import json
import re

sout = getwriter("utf8")(stdout)

class SportPipeline(object):

    def address_formatter(self, value):
        data = value.split(u'<br>')
        res = ''
        for d in data:
            res += ' ' + d.strip()
        return res

    def process_item(self, item, spider):
        row = {}
        row["name"] = ''.join(item['name']).strip()
        row["category"] = item['category']
        row["address"] = self.address_formatter(''.join(item['address']))
        sout.write(json.dumps(row, ensure_ascii=False) + "\n")