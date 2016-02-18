# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from sys import stdout
import time

import re
from codecs import getwriter
from lxml import etree
from scrapy.exceptions import DropItem

sout = getwriter("utf8")(stdout)


class FsvpsPipeline(object):

    def __init__(self):
        self.count_item = 0
        self.ns = {"xi": 'http://www.w3.org/2001/XInclude'}
        self.xml = etree.Element('companies', version='2.1', nsmap=self.ns)

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

    def validate_phones(self, value):
        phones = []
        if not value:
            return phones

        for tels in value:
            phns = tels.split(',')
            for phone in phns:
                number = re.sub("\D", '', phone).strip()
                phones.append(number)
        return phones

    def validate_address(self, value):
        try_split = re.split(u'\d+,?', value)
        if len(try_split) > 1:
            addr = try_split[1]
        else:
            addr = try_split[0]

        return addr

    def validate_otdel_name(self,name,type):
        if type == 1:
            return True
        keywords = [u"Межрайонный",u"надзор",u"контрол"]
        pattern = '|'.join(keywords)
        if re.search(pattern,name,re.IGNORECASE):
            return True
        else:
            return False


    def process_item(self, item, spider):

        name = self.validate_str(item['name'])

        type = item['type']

        if not self.validate_otdel_name(name,type):
            raise DropItem

        url = item['url']


        if type == 1:
            address = self.validate_str(item['address'])
            address = self.validate_address(address)
            email = self.validate_str(item['email'])
        else:
            content = item["content"]
            address = "Test adress"
            email = "Test"

        xml_item = etree.SubElement(self.xml, 'company')
        xml_id = etree.SubElement(xml_item, 'company_id')
        xml_id.text = "34324"

        xml_name = etree.SubElement(xml_item, 'name', lang=u'ru')
        xml_name.text = name

        xml_address = etree.SubElement(xml_item, 'address')
        xml_address.text = address

        xml_country = etree.SubElement(xml_item, 'country', lang=u'ru')
        xml_country.text = u'Россия'

        xml_email = etree.SubElement(xml_item, 'email')
        xml_email.text = email

        xml_url = etree.SubElement(xml_item, 'url', lang=u'ru')
        xml_url.text = url

        xml_rubric = etree.SubElement(xml_item, 'rubric-id')
        xml_rubric.text = u"184105646"

        xml_date = etree.SubElement(xml_item, 'actualization-date')
        xml_date.text = unicode(int(round(time.time() * 1000)))

        self.count_item +=1
        xml_count = etree.SubElement(xml_item, 'coun-item')
        xml_count.text = unicode(self.count_item)


    def close_spider(self, spider):
        doc = etree.tostring(self.xml, pretty_print=True, encoding='unicode')
        sout.write('<?xml version="1.0" encoding="UTF-8" ?>' + '\n')
        sout.write(doc)
