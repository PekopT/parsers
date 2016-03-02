# -*- coding: utf-8 -*-
import time
import StringIO
import re
from codecs import getwriter
from sys import stdout
from lxml import etree

from scrapy.exceptions import DropItem
from schema_org import SCHEMA_ORG

sout = getwriter("utf8")(stdout)

relaxng_doc = etree.parse(SCHEMA_ORG)
relaxng = etree.RelaxNG(relaxng_doc)

BY_TYL_CODES = [unicode(x) for x in (
    17,
    29,
    44,
    33,
)]

KZ_TYL_CODES = [unicode(x) for x in (
    700,
    727,
    725,
    701,
    7262,

)]


class LagunaPipeline(object):
    def __init__(self):
        self.count_item = 0
        self.ns = {"xi": 'http://www.w3.org/2001/XInclude'}
        self.xml = etree.Element('companies', version='2.1', nsmap=self.ns)

    def company_id(self):
        return u'0199' + unicode(self.count_item)

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
            if ';' in phone:
                phns = phone.split(';')
            else:
                phns = phone.split(',')

            for ph in phns:
                if ph.strip():
                    ph = ph.strip()
                    phone = re.sub('\D', '', ph)
                    phones.append(u"+380 (44) " + phone)

        return phones

    def delete_tags(self,value):
        pattern = u'\<[^>]*\>'
        value = re.sub(pattern,'',value)
        value = re.sub(u'&#13;|&lt;|&gt;|<|>|\/li|\r','',value)
        value = re.sub(u'td|span|\/|br','',value)
        return value


    def validate_phones(self, value,type):
        phones = []
        if not value:
            return []
        if ';' in value:
            phns = value.split(';')
        else:
            phns = value.split(',')

        for ph in phns:
            if ph.strip():
                ph = ph.strip()
                phone = re.sub('\D', '', ph)
                if type == 1:
                    for code in BY_TYL_CODES:
                        if phone.find(code) == 3:
                            phone = u"+375" + u" (" + code + u") " + re.sub("^375%s" % code, '', phone)
                            break
                else:
                    phone = re.sub('^7','',ph)
                    phone = re.sub('^8','',phone)
                    for code in KZ_TYL_CODES:
                        if phone.find(code) == 0:
                            phone = u"+8" + u" (" + code + u") " + re.sub("^%s" % code, '', phone)
                            break

                phones.append(phone)

        return phones

    def process_item(self, item, spider):
        name = u"Лагуна"
        address = ''.join(item['address'])
        phones = ''.join(item['phone'])
        url = item['url']
        type = item['type']
        country = item['country']
        oblast = item['oblast'].strip()
        working_time = ''.join(item['working_time'])

        w_items = working_time.split('<br>')

        w_str = ''
        for w in w_items:
            m = re.search(u'выход',w)
            if not m:
                w_str += w

        working_time = w_str

        phone_items = phones.split('<br>')

        p_str = ''
        for p in phone_items:
            p_str += self.delete_tags(p)

        city = ''.join(item['city'])
        city = self.delete_tags(city)
        address = self.delete_tags(address)
        working_time = self.delete_tags(working_time)

        self.count_item += 1
        xml_item = etree.SubElement(self.xml, 'company')
        xml_id = etree.SubElement(xml_item, 'company-id')
        xml_id.text = self.company_id()

        xml_name = etree.SubElement(xml_item, 'name', lang=u'ru')
        xml_name.text = name

        xml_address = etree.SubElement(xml_item, 'address', lang=u'ru')
        address_out = oblast + u',город ' + city + ',' + address
        address_out = re.sub('\(|\)','',address_out)
        xml_address.text = address_out.strip(', ')

        xml_country = etree.SubElement(xml_item, 'country', lang=u'ru')
        xml_country.text = country

        # xml_city = etree.SubElement(xml_item, 'city', lang=u'ru')
        # xml_city.text = oblast.strip()

        # xml_phone_raw = etree.SubElement(xml_item, 'phone_raw', lang=u'ru')
        # xml_phone_raw.text = p_str

        ch_phone =  re.sub('\D','',p_str).strip()
        if not ch_phone:
            raise DropItem

        for phone in self.validate_phones(p_str,type):
            xml_phone = etree.SubElement(xml_item, 'phone')
            xml_phone_number = etree.SubElement(xml_phone, 'number')
            xml_phone_number.text = phone.strip()
            xml_phone_type = etree.SubElement(xml_phone, 'type')
            xml_phone_type.text = u'phone'
            xml_phone_ext = etree.SubElement(xml_phone, 'ext')
            xml_phone_info = etree.SubElement(xml_phone, 'info')

        xml_url = etree.SubElement(xml_item, 'url')
        xml_url.text = url

        if working_time:
            xml_working_time = etree.SubElement(xml_item, 'working-time',lang=u"ru")
            xml_working_time.text = working_time

        xml_rubric = etree.SubElement(xml_item, 'rubric-id')
        xml_rubric.text = u"184107871"

        xml_date = etree.SubElement(xml_item, 'actualization-date')
        xml_date.text = unicode(int(round(time.time() * 1000)))


    def close_spider(self, spider):
        doc = etree.tostring(self.xml, pretty_print=True, encoding='unicode')
        sout.write('<?xml version="1.0" encoding="UTF-8" ?>' + '\n')
        sout.write(doc)
