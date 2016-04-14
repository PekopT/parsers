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

        val = val.replace('Boy: ', '').replace('Ya\u015f: ', '').replace('\n', ' ').replace('\r', '').replace('\t', '')
        val = re.sub(' +', ' ', val)
        if len(val.split('(')) > 1:
            val = val.split('(')[0]
        return val.strip()

    def process_item(self, item, spider):
        height = float(self.validate_int(item['height'], length=3)) / 100
        weight = int(self.validate_int(item['weight'], length=2))
        name = self.validate_str(item['name']) or ''
        desc = self.validate_str(item['desc']) or ''


        if (height is None and weight is None) or name.replace(' ', '-') == '':
            raise DropItem("Missing weight and height in %s" % item)

        ids_url = item['url'] + '#' + name.replace(' ', '-')

        human = {}
        human["ontoid"] = u"ext_unluyaslari_" + name.replace(' ', '-')
        human["ids"] =({
                    "type": u"url",
                    "value": ids_url,
                    "langua": u"tr"
        },)
        human["Title"] = ({"value": name},)
        human["params"] = {
                "Height": ({
                        "value": unicode(height),
                        "unit": u"m"
                    },),
                # "Weight": ({
                #         "value": unicode(weight),
                #         "unit": u"kg"
                #     },)
        }

        human["isa"] = {}
        human["isa"]["otype"] = ({"value": u"Hum"})
        if desc:
            human["isa"]["ShortDefin"] = ({
                        "lang": u"tr",
                        "value": desc
            },)

        sout = getwriter("utf8")(stdout)
        sout.write(json.dumps(human, ensure_ascii=False) + "\n")
