# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from codecs import getwriter
from sys import stdout
import json

import re
from scrapy.exceptions import DropItem


class UnluyaslariPipeline(object):
    def validate_int(self, value, length, suffix=False):
        if type(value) == list:
            val = value[0] if value else None
            if val is None:
                return False
        else:
            val = value

        if length is not False:
            val = re.sub("\D", "", val)
            if len(val) != length:
                return False
        return val.strip()

    def validate_str(self, value):
        if type(value) == list:
            for v in value:
                if v.strip():
                    val = v.strip()
                    break
                else:
                    val = None
            if val is None:
                return False
        else:
            val = value

        val = val.replace('Boy: ', '').replace('Ya\u015f: ', '')
        if len(val.split('(')) > 1:
            val = val.split('(')[0]
        return val.strip()

    def process_item(self, item, spider):
        height = float(self.validate_int(item['height'], length=3)) / 100
        weight = int(self.validate_int(item['weight'], length=2))
        name = self.validate_str(item['name']) or ''
        desc = self.validate_str(item['desc']) or ''

        if height is None and weight is None:
            raise DropItem("Missing weight and height in %s" % item)

        human = {
            "ontoid": u"ext_unluyaslari_" + name.replace(' ', '-'),
            "ids": (
                {
                    "type": u"url",
                    "value": item['url'],
                    "langua": u"tr"
                },
            ),
            "Title": (
                {
                    "value": name
                },
            ),
            "params": {
                "Height": (
                    {
                        "value": height,
                        "unit": u'm'
                    },
                ),
                "Weight": (
                    {
                        "value": weight,
                        "unit": u"kg",
                    },
                )
            },
            "isa": {
                "ShortDefin": (
                    {
                        "lang": u"tr",
                        "value": desc
                    },
                ),
                "otype": (
                    {
                        "value": u"Hum"
                    },
                )
            }
        }

        sout = getwriter("utf8")(stdout)
        sout.write(json.dumps(human, ensure_ascii=False) + "\n")
