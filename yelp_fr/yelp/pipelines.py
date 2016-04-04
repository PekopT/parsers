# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from codecs import getwriter
from sys import stdout
import json

import re


class YelpPipeline(object):

    def process_item(self, item, spider):

        human = {
            "name": ''.join(item['name']).strip(),
            "category":','.join(item['category']).strip(),
            "adress": ','.join(item['adress']).strip()
        }

        sout = getwriter("utf8")(stdout)
        sout.write(json.dumps(human, ensure_ascii=False) + "\n")