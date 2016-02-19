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

from phonecodes import BY_TYL_CODES


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
            return []

        for phone in value:
            phns = phone.split(',')
            for phone in phns:
                if phone.strip():
                    phone = re.sub('\D','',phone)
                    phone = re.sub("^8", '', phone)
                    for code in BY_TYL_CODES:
                        if phone.find(code) == 0:
                            phones.append(u"+7" + u" (" + code + u") " + re.sub("^%s" % code, '', phone))
                            status = True
                            break
                    if not status:
                        phones.append(phone)


        return phones

    def validate_address(self, value):
        try_split = re.split(u'\d+,?', value)
        if len(try_split) > 1:
            addr = try_split[1]
        else:
            addr = try_split[0]
        return addr


    def remove_postal(self,value):
        value = re.sub(r"\d{6}",'',value)
        value = re.sub(u"«|»|\(|\)",'',value)
        value = re.sub(u'&#13;|&lt;|&gt;|\/li','',value)
        value.rstrip(',) ')
        return value



    def validate_otdel_name(self,name,type):
        if type == 1:
            return True
        keywords = [u"Межрайонный",u"надзор",u"контрол"]
        pattern = '|'.join(keywords)
        if re.search(pattern,name,re.IGNORECASE):
            return True
        else:
            return False

    def split_organization(self,value):
        new_value = re.sub(u"\s+", '', value)
        address = new_value.split(u'г.')
        if len(address) > 2:
            del address[0]
            address[0] = u'г.' + address[0]
            address[1] = u'г.' + address[1]
            return address
        else:
            return [value]

    def get_phone_from_content(self,value):
        phones = []
        items = value.split('<br>')
        for item in items:
            if re.search(u'тел|Тел', item, re.IGNORECASE):
                phone = item.strip()
                phns = re.split('; |,', phone)
                for ph in phns:
                    phone = re.sub('\D', '', ph)
                    phones.append(phone)

        return phones

    def get_address_from_content(self,value):
        address_coll = []
        items = value.split('<br>')
        for item in items:
            item = item.strip()
            if not re.search(u'span',item):
                if not re.search(u'(^\(|\)$)',item):
                    if re.search(u"(г\.|ст\.|п\.|с\.|ул\.)", item,re.IGNORECASE):
                        address_coll.append(item)

        if len(address_coll) > 0:
            return address_coll[0]
        else:
            return u''


    def process_item(self, item, spider):
        name = self.validate_str(item['name'])
        type = item['type']
        if not self.validate_otdel_name(name, type):
            raise DropItem
        
        url = item['url']
        if type == 1:
            address = self.validate_str(item['address'])
            address = self.remove_postal(self.validate_address(address))
            email = self.validate_str(item['email'])
            phones = item['phone']
        else:
            content = item["content"]
            address = self.remove_postal(self.get_address_from_content(content))
            phones = self.get_phone_from_content(content)
            email = ""

        organizations = self.split_organization(address)

        xml_item = etree.SubElement(self.xml, 'company')
        xml_id = etree.SubElement(xml_item, 'company_id')
        xml_id.text = "34324"

        xml_name = etree.SubElement(xml_item, 'name', lang=u'ru')
        xml_name.text = name

        address = organizations[0].rstrip(',.; ').lstrip(',( ')

        if address:
            xml_address = etree.SubElement(xml_item, 'address')
            xml_address.text = address

        xml_country = etree.SubElement(xml_item, 'country', lang=u'ru')
        xml_country.text = u'Россия'

        for phone in self.validate_phones(phones):
            xml_phone = etree.SubElement(xml_item, 'phone')
            xml_phone_number = etree.SubElement(xml_phone, 'number')
            xml_phone_number.text = phone.strip()
            xml_phone_type = etree.SubElement(xml_phone, 'type')
            xml_phone_type.text = u'phone'
            xml_phone_ext = etree.SubElement(xml_phone, 'ext')
            xml_phone_info = etree.SubElement(xml_phone, 'info')


        if email:
            xml_email = etree.SubElement(xml_item, 'email')
            xml_email.text = email

        xml_url = etree.SubElement(xml_item, 'url', lang=u'ru')
        xml_url.text = url

        xml_rubric = etree.SubElement(xml_item, 'rubric-id')
        xml_rubric.text = u"184105646"

        xml_date = etree.SubElement(xml_item, 'actualization-date')
        xml_date.text = unicode(int(round(time.time() * 1000)))

        self.count_item +=1
        xml_count = etree.SubElement(xml_item, 'count-item')
        xml_count.text = unicode(self.count_item)


        if (len(organizations) > 1):
            xml_item2 = etree.SubElement(self.xml, 'company')
            xml_id2 = etree.SubElement(xml_item2, 'company_id')
            xml_id2.text = "34324"

            xml_name2 = etree.SubElement(xml_item2, 'name', lang=u'ru')
            xml_name2.text = name
            xml_address2 = etree.SubElement(xml_item2, 'address')
            xml_address2.text = organizations[1].rstrip(',.; ').lstrip(',( ')

            xml_url2 = etree.SubElement(xml_item2, 'url', lang=u'ru')
            xml_url2.text = url

            self.count_item +=1
            xml_count2 = etree.SubElement(xml_item2, 'count-item')
            xml_count2.text = unicode(self.count_item)



    def close_spider(self, spider):
        doc = etree.tostring(self.xml, pretty_print=True, encoding='unicode')
        sout.write('<?xml version="1.0" encoding="UTF-8" ?>' + '\n')
        sout.write(doc)
