# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import time
import re
from codecs import getwriter
from sys import stdout
from lxml import etree
from scrapy.exceptions import DropItem

sout = getwriter("utf8")(stdout)


class UkrtelecomPipeline(object):

    def __init__(self):
        self.count_item = 0
        self.ns = {"xi": 'http://www.w3.org/2001/XInclude'}
        self.xml = etree.Element('companies', version='2.1', nsmap=self.ns)

    def company_id(self):
        return u'0009' + unicode(self.count_item)

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


    def formatter_workin_time(self,value):
        if type(value) == list:
            val = u""
            for v in value:
                if v.strip():
                    val_temp = v.strip()
                    if not re.search(u"вихід",val_temp):
                        val += u"," + v.strip()

            if val is None:
                return u""
        else:
            val = value

        return val.strip()

    def process_item(self, item, spider):
        name = item['name']
        url = item['url']
        phone = item['phone']
        city = item['city']

        working_time = self.formatter_workin_time(item['working_time'])

        address = u"город " + self.validate_str(item['city']) + u" , " +self.validate_str(item['address'])

        self.count_item +=1

        xml_item = etree.SubElement(self.xml, 'company')
        xml_id = etree.SubElement(xml_item, 'company_id')
        xml_id.text = self.company_id()

        xml_name = etree.SubElement(xml_item, 'name', lang=u'ua')
        xml_name.text = name

        address = address
        xml_address = etree.SubElement(xml_item, 'address', lang=u'ua')
        xml_address.text = address

        xml_phone = etree.SubElement(xml_item, 'phone')
        xml_phone_number = etree.SubElement(xml_phone, 'number')
        xml_phone_number.text = phone.strip()
        xml_phone_type = etree.SubElement(xml_phone, 'type')
        xml_phone_type.text = u'phone'

        xml_phone_ext = etree.SubElement(xml_phone, 'ext')
        xml_phone_info = etree.SubElement(xml_phone, 'info')

        xml_working_time = etree.SubElement(xml_item, 'working-time', lang=u'ua')
        xml_working_time.text = working_time[1:]

        xml_url = etree.SubElement(xml_item, 'url')
        xml_url.text = url

        xml_rubric = etree.SubElement(xml_item, 'rubric-id')
        xml_rubric.text = u"184107799"

        xml_date = etree.SubElement(xml_item, 'actualization-date')
        xml_date.text = unicode(int(round(time.time() * 1000)))

    def close_spider(self, spider):
        doc = etree.tostring(self.xml, pretty_print=True, encoding='unicode')
        sout.write('<?xml version="1.0" encoding="UTF-8" ?>' + '\n')
        sout.write(doc)
