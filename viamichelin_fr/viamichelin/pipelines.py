# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from codecs import getwriter
from sys import stdout
import json
import re

from utils import check_spider_close, check_spider_pipeline


sout = getwriter("utf8")(stdout)
class JsonPipeline(object):
    def __init__(self):
        self.data = []

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
        value = re.sub(u'td|span|\/|br', '', value)
        return value

    @check_spider_close
    def close_spider(self, spider):
        sout = getwriter("utf8")(stdout)



class HotelPipeline(JsonPipeline):

    @check_spider_pipeline
    def process_item(self, item, spider):
        row = {}
        row["name"] = ''.join(item["name"]).strip()
        row["category"] = u"Hotel"
        row["address"] = ''.join(item["address"]).strip()

        sout.write(json.dumps(row, ensure_ascii=False) + "\n")


class RestaurantPipeline(JsonPipeline):

    @check_spider_pipeline
    def process_item(self, item, spider):
        row = {}
        row["name"] = ''.join(item["name"]).strip()
        row["category"] = u"restaurant"
        row["address"] = ''.join(item["address"]).strip()
        sout.write(json.dumps(row, ensure_ascii=False) + "\n")


