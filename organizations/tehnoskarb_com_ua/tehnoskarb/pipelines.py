# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import time
import StringIO
import re
from codecs import getwriter
from sys import stdout
from lxml import etree

from scrapy.exceptions import DropItem
from schema_org import SCHEMA_ORG
from utils import UA_TYL_CODES, UA_CITIES_UKR, UA_CITIES_RUS

sout = getwriter("utf8")(stdout)

relaxng_doc = etree.parse(SCHEMA_ORG)
relaxng = etree.RelaxNG(relaxng_doc)


class TehnoskarbPipeline(object):
    def __init__(self):
        self.count_item = 0
        self.ns = {"xi": 'http://www.w3.org/2001/XInclude'}
        self.xml = etree.Element('companies', version='2.1', nsmap=self.ns)

    def company_id(self):
        return u'0099' + unicode(self.count_item)

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

    def validate_tel(self, value):
        phones = []
        if not value:
            return []

        for phone in value:
            if phone.strip():
                phone = phone.strip()
                phone = re.sub('\D', '', phone)
                phone = re.sub('^0', '', phone)
                for code in UA_TYL_CODES:
                    if phone.find(code) == 0:
                        phone = u"+380" + u" (" + code + u") " + re.sub("^%s" % code, '', phone)
                        break
                if phone:
                    phones.append(phone)

        return phones

    def validate_rus_address(self, value):
        pattern = u'г\.\s*[А-Яа-я-\s]+'
        m = re.search(pattern,value)
        if m:
            city = m.group(0)
            city = re.sub(u'г\.\s*','',city)
        else:
            city = u''

        region = self.get_region(city, UA_CITIES_RUS) or u""

        if region:
            address = region + u' область, город '+ city + re.sub(pattern,'',value)
        else:

            address = u'город ' + city + re.sub(pattern,'',value)
        return address


    def validate_ua_address(self, value):
        pattern = u'м\s*\.\s*[А-Яа-я-іїєґІЇЄ\s]+'
        m = re.search(pattern, value)
        if m:
            city = m.group(0)
            city = re.sub(u'м\s*\.\s*','',city)
        else:
            city = u''

        region = self.get_region(city, UA_CITIES_UKR) or u""

        if region:
            address = region + u', мисто '+ city + re.sub(pattern,'',value)
        else:
            if u"Кам'янець-Подільський" in value:
                address = u'Хмельницька область, мисто '+ city + re.sub(pattern, '', value)
            else:
                address = u'мисто ' + city + re.sub(pattern,'',value)
        return address


    def get_region(self, city, cities):
        for k, v in cities.iteritems():
            if city in v:
                return k
        return False


    def process_item(self, item, spider):
        name = u"Техноскарб"
        name_ua = u"Техноскарб"
        url_rus = item['add_url_ru']
        url_ua = item['add_url_ua']
        address_rus = ''.join(item['address_rus'])
        address_ua = ''.join(item['address_ua'])
        phones = item['phone']
        working_time_ru = ''.join(item['working_time_ru'])
        working_time_ua = ''.join(item['working_time_ua'])

        self.count_item += 1
        xml_item = etree.SubElement(self.xml, 'company')
        xml_id = etree.SubElement(xml_item, 'company-id')
        xml_id.text = self.company_id()

        xml_name = etree.SubElement(xml_item, 'name', lang=u'ru')
        xml_name.text = name

        xml_name_ua = etree.SubElement(xml_item, 'name', lang=u'ua')
        xml_name_ua.text = name_ua

        xml_address_rus = etree.SubElement(xml_item, 'address_rus', lang=u'ru')
        address_rus = self.validate_rus_address(address_rus)
        xml_address_rus.text = re.sub('\(|\)', '', address_rus)

        xml_address_ua = etree.SubElement(xml_item, 'address_ua', lang=u'ua')
        address_ua = self.validate_ua_address(address_ua)
        xml_address_ua.text = re.sub('\(|\)', '', address_ua)


        xml_country = etree.SubElement(xml_item, 'country', lang=u'ru')
        xml_country.text = u"Украина"

        xml_country2 = etree.SubElement(xml_item, 'country', lang=u'ua')
        xml_country2.text = u"Україна"

        for phone in self.validate_tel(phones):
            xml_phone = etree.SubElement(xml_item, 'phone')
            xml_phone_number = etree.SubElement(xml_phone, 'number')
            xml_phone_number.text = phone.strip()
            xml_phone_type = etree.SubElement(xml_phone, 'type')
            xml_phone_type.text = u'phone'
            xml_phone_ext = etree.SubElement(xml_phone, 'ext')
            xml_phone_info = etree.SubElement(xml_phone, 'info')

        xml_url = etree.SubElement(xml_item, 'url')
        xml_url.text = "http://tehnoskarb.com.ua/"

        xml_url_ru = etree.SubElement(xml_item, 'add-url')
        xml_url_ru.text = url_rus

        xml_url_ua = etree.SubElement(xml_item, 'add-url')
        xml_url_ua.text = url_ua

        xml_working_time_rus = etree.SubElement(xml_item, 'working_time', lang=u'ru')
        xml_working_time_rus.text = working_time_ru

        xml_working_time_ua = etree.SubElement(xml_item, 'working_time', lang=u'ua')
        xml_working_time_ua.text = working_time_ua

        xml_rubric = etree.SubElement(xml_item, 'rubric-id')
        xml_rubric.text = u"184107929"

        xml_rubric2 = etree.SubElement(xml_item, 'rubric-id')
        xml_rubric2.text = u"184107853"

        xml_rubric3 = etree.SubElement(xml_item, 'rubric-id')
        xml_rubric3.text = u"184107835"

        xml_date = etree.SubElement(xml_item, 'actualization-date')
        xml_date.text = unicode(int(round(time.time() * 1000)))

        company_valid = etree.tostring(xml_item, pretty_print=True, encoding='unicode')
        company_valid = StringIO.StringIO(company_valid)
        valid = etree.parse(company_valid)
        # if not relaxng.validate(valid):
        #     raise DropItem

    def close_spider(self, spider):
        doc = etree.tostring(self.xml, pretty_print=True, encoding='unicode')
        sout.write('<?xml version="1.0" encoding="UTF-8" ?>' + '\n')
        sout.write(doc)
