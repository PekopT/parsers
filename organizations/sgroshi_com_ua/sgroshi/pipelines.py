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


class SgroshiPipeline(object):
    def __init__(self):
        self.count_item = 0
        self.ns = {"xi": 'http://www.w3.org/2001/XInclude'}
        self.xml = etree.Element('companies', version='2.1', nsmap=self.ns)

    def company_id(self, value):
        str_for_hash = value
        hash_for_address = abs(hash(str_for_hash))
        return unicode(hash_for_address)

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

        value = value.split(',')
        for phone in value:
            if phone.strip():
                phone = phone.strip()
                phone = re.sub('\D', '', phone)
                if "0800501020" in phone:
                    continue
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
                return k + ","
        return False

    def delete_tags(self, value):
        pattern = u'\<[^>]*\>'
        value = re.sub(pattern, '', value)
        value = re.sub(u'&#13;|&lt;|&gt;|<|>|\/li|\r', '', value)
        value = re.sub(u'td|span|br', '', value)
        return value

    def delete_brackets(self, value):
        pattern = u'\(.*\)'
        value = re.sub(pattern, '', value)
        return value

    def get_address_info(self, address):
        info = u''
        pattern = u'\(.*\)'
        m = re.search(pattern, address)
        if m:
            info = m.group(0)
        return info

    def get_number_from_street(self, value):
        value = re.sub(u'50 лет',u'', value)
        value = re.sub(u'20\-го',u'', value)
        value = re.sub(u'50\-річчя',u'', value)
        value = re.sub(u'20 Парт',u'', value)
        s_val = u''
        m = re.search(u'(\s+[0-9-]+)', value)
        if m:
            s_val = m.group(0)
        return s_val

    def process_item(self, item, spider):
        name = u"ШвидкоГрошi"
        name_ua = u"ШвидкоГрошi"
        url = item['url']
        address = item['address']
        address_ua = item['address_ua']
        city = ''.join(item['city'])
        city_ua = ''.join(item['city_ua'])
        phones = ''.join(item['phone'])

        # to_replace = u"\<strong\>.+\<\/strong\>"
        # address = re.sub(to_replace, u'', address)
        # address = self.delete_tags(address)
        # tc = self.get_address_info(address)
        # address = address.replace(tc, '')
        region = self.get_region(city, UA_CITIES_RUS) or ""
        # n_for_address = self.get_number_from_street(address)
        # if n_for_address:
        #     address = address.replace(n_for_address, u',' + n_for_address.strip())
        #     address = re.sub(u'(\,){2,}', u',', address)
        address = region + u'город ' + city + u',' + address
        # address = re.sub(u'\(|\)|\«|\»|\"', '', address).strip()

        self.count_item += 1
        xml_item = etree.SubElement(self.xml, 'company')
        xml_id = etree.SubElement(xml_item, 'company-id')
        xml_id.text = self.company_id(address)

        xml_name = etree.SubElement(xml_item, 'name', lang=u'ru')
        xml_name.text = name

        xml_name_ua = etree.SubElement(xml_item, 'name', lang=u'ua')
        xml_name_ua.text = name_ua

        xml_address = etree.SubElement(xml_item, 'address', lang=u'ru')
        xml_address.text = address

        address_add_ru = item['address_add_ru']
        if address_add_ru:
            xml_address_add = etree.SubElement(xml_item, 'address-add', lang=u"ru")
            tc = re.sub(u'\(|\)|\«|\»|\"', '', address_add_ru)
            xml_address_add.text = tc

        region_ua = self.get_region(city_ua, UA_CITIES_UKR) or ""
        address_ua = region_ua + u'мисто ' + city_ua + u',' + address_ua
        xml_address_ua = etree.SubElement(xml_item, 'address', lang=u'ua')
        address_ua = re.sub(u'\(|\)|\«|\»|\"', '', address_ua).strip()
        xml_address_ua.text = address_ua

        address_add_ua = item['address_add_ua']
        if address_add_ua:
            xml_address_add_ua = etree.SubElement(xml_item, 'address-add', lang=u"ua")
            tc_ua = re.sub(u'\(|\)|\«|\»|\"', '', address_add_ua)
            xml_address_add_ua.text = tc_ua

        xml_country = etree.SubElement(xml_item, 'country', lang=u'ru')
        xml_country.text = u"Украина"
        xml_country2 = etree.SubElement(xml_item, 'country', lang=u'ua')
        xml_country2.text = u"Україна"
        #
        xml_phone_main = etree.SubElement(xml_item, 'phone')
        xml_phone_number_main = etree.SubElement(xml_phone_main, 'number')
        xml_phone_number_main.text = "0 (800) 50-10-20"
        xml_phone_type = etree.SubElement(xml_phone_main, 'type')
        xml_phone_type.text = u'phone'
        xml_phone_ext = etree.SubElement(xml_phone_main, 'ext')
        xml_phone_info = etree.SubElement(xml_phone_main, 'info')

        for phone in self.validate_tel(phones):
            xml_phone = etree.SubElement(xml_item, 'phone')
            xml_phone_number = etree.SubElement(xml_phone, 'number')
            xml_phone_number.text = phone.strip()
            xml_phone_type = etree.SubElement(xml_phone, 'type')
            xml_phone_type.text = u'phone'
            xml_phone_ext = etree.SubElement(xml_phone, 'ext')
            xml_phone_info = etree.SubElement(xml_phone, 'info')

        xml_url = etree.SubElement(xml_item, 'url')
        xml_url.text = u"http://sgroshi.com.ua"
        #
        working_time_ru = item['working_time']
        working_time_ru = working_time_ru.replace("Su -","")\
            .replace("Mo-Fr", u"Пн-Пт")\
            .replace("Sa",u"Сб").replace("Su",u"Вс").strip(", ")

        working_time_ua = item['working_time']
        working_time_ua = working_time_ua.replace("Su -","")\
            .replace("Mo-Fr", u"Пн-Пт")\
            .replace("Sa",u"Сб").replace("Su",u"Нд").strip(", ")

        xml_working_time_rus = etree.SubElement(xml_item, 'working-time', lang=u'ru')
        xml_working_time_rus.text = working_time_ru

        xml_working_time_ua = etree.SubElement(xml_item, 'working-time', lang=u'ua')
        xml_working_time_ua.text = working_time_ua

        xml_rubric = etree.SubElement(xml_item, 'rubric-id')
        xml_rubric.text = u"184105574"

        xml_date = etree.SubElement(xml_item, 'actualization-date')
        xml_date.text = unicode(int(round(time.time() * 1000)))
        #
        # company_valid = etree.tostring(xml_item, pretty_print=True, encoding='unicode')
        # company_valid = StringIO.StringIO(company_valid)
        # valid = etree.parse(company_valid)
        # if not relaxng.validate(valid):
        #     raise DropItem

    def close_spider(self, spider):
        doc = etree.tostring(self.xml, pretty_print=True, encoding='unicode')
        sout.write('<?xml version="1.0" encoding="UTF-8" ?>' + '\n')
        sout.write(doc)
