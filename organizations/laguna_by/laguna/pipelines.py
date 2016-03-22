# -*- coding: utf-8 -*-
import time
import StringIO
import re
from codecs import getwriter
from sys import stdout
from lxml import etree

from scrapy.exceptions import DropItem
from schema_org import SCHEMA_ORG
from utils import check_spider_close, check_spider_pipeline

sout = getwriter("utf8")(stdout)

relaxng_doc = etree.parse(SCHEMA_ORG)
relaxng = etree.RelaxNG(relaxng_doc)

BY_TYL_CODES = [unicode(x) for x in (
    17,
    29,
    44,
    232,
    33,
    152,
    163,
    164,
    222,
    212,
    214,
    216,
)]

KZ_TYL_CODES = [unicode(x) for x in (
    700,
    727,
    725,
    701,
    7262,

)]


class XmlPipeline(object):
    counter = 0

    def __init__(self):
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

    def delete_tags(self, value):
        pattern = u'\<[^>]*\>'
        value = re.sub(pattern, '', value)
        value = re.sub(u'&#13;|&lt;|&gt;|<|>|\/li|\r\n', '', value)
        value = re.sub(u'td|span|\/|br', '', value)
        return value

    def validate_phones(self, value, type):
        phones = []
        if not value or not re.sub('\D', '', value).strip():
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
                    phone = re.sub('^7', '', ph)
                    phone = re.sub('^8', '', phone)
                    for code in KZ_TYL_CODES:
                        if phone.find(code) == 0:
                            phone = u"+8" + u" (" + code + u") " + re.sub("^%s" % code, '', phone)
                            break

                phones.append(phone)

        return phones

    def format_address(self, address, oblast, city):
        if u'г.п.' not in city and u'р-н' not in city:
            address_out = oblast + u',город ' + city + ',' + address
        else:
            address_out = oblast + u',' + city + ',' + address
        address_out = re.sub('\(|\)', '', address_out)
        return address_out

    def get_tc(self, value):
        tc = u''
        value += ','
        m = re.search(u'ТЦ\s*[А-Я а-я \d \s « » "]+\,', value)
        if m:
            tc = m.group(0)
        return tc

    @check_spider_close
    def close_spider(self, spider):
        doc = etree.tostring(self.xml, pretty_print=True, encoding='unicode')
        sout.write('<?xml version="1.0" encoding="UTF-8" ?>' + '\n')
        sout.write(doc)



class LagunaBelPipeline(XmlPipeline):

    @check_spider_pipeline
    def process_item(self, item, spider):
        address = ''.join(item['address'])
        phones = ''.join(item['phone'])
        url = item['url']
        type = item['type']
        country = item['country']
        oblast = item['oblast'].strip()
        working_time = ''.join(item['working_time'])
        w_items = working_time.split('<br>')

        new_works = []
        for w in w_items:
            w = self.delete_tags(w).rstrip(';')
            w_list = w.split(';')
            if len(w_list) == 1:
                new_works.append(w_list[0] + ';')
            elif len(w_list) > 1:
                for nw in w_list:
                    if nw.strip():
                        new_works.append(nw.strip() + ';')


        w_str = ''
        for w in new_works:
            m = re.search(u'выход', w)
            if not m:
                w_str += w
        working_time = w_str[:-1]

        phone_items = phones.split('<br>')
        p_str = ''
        for p in phone_items:
            p_str += self.delete_tags(p)

        city = ''.join(item['city'])
        city = self.delete_tags(city)
        address = self.delete_tags(address)
        working_time = self.delete_tags(working_time)

        address_out = self.format_address(address, oblast, city)
        tc = self.get_tc(address_out)

        address_out = address_out.replace(tc, '')
        address_out = address_out.replace(tc[:-1], '')
        address_out = address_out.replace("www.dom35.by", '')
        address_out = address_out.strip(', ')

        self.counter += 1
        xml_item = etree.SubElement(self.xml, 'company')
        xml_id = etree.SubElement(xml_item, 'company-id')
        xml_id.text = self.company_id(address_out)

        xml_name = etree.SubElement(xml_item, 'name', lang=u'ru')
        xml_name.text = u"Лагуна"


        xml_address = etree.SubElement(xml_item, 'address', lang=u'ru')
        xml_address.text = address_out

        if tc:
            tc = re.sub(u'\"|\«|\»', ' ', tc)
            xml_address_add = etree.SubElement(xml_item,'address-add', lang=u"ru")
            tc = tc[:-1].strip()
            tc = re.sub(u'\s{2,}', u' ', tc)
            xml_address_add.text = tc

        xml_country = etree.SubElement(xml_item, 'country', lang=u'ru')
        xml_country.text = country

        for phone in self.validate_phones(p_str, type):
            xml_phone = etree.SubElement(xml_item, 'phone')
            xml_phone_number = etree.SubElement(xml_phone, 'number')
            xml_phone_number.text = phone.strip()
            xml_phone_type = etree.SubElement(xml_phone, 'type')
            xml_phone_type.text = u'phone'
            xml_phone_ext = etree.SubElement(xml_phone, 'ext')
            xml_phone_info = etree.SubElement(xml_phone, 'info')

        xml_url = etree.SubElement(xml_item, 'url')
        xml_url.text = u"http://www.laguna.by/"

        xml_url_add = etree.SubElement(xml_item, 'add-url')
        xml_url_add.text = url

        if working_time:
            xml_working_time = etree.SubElement(xml_item, 'working-time', lang=u"ru")
            xml_working_time.text = working_time

        xml_rubric = etree.SubElement(xml_item, 'rubric-id')
        xml_rubric.text = u"184107871"

        xml_date = etree.SubElement(xml_item, 'actualization-date')
        xml_date.text = unicode(int(round(time.time() * 1000)))


        company_valid = etree.tostring(xml_item, pretty_print=True, encoding='unicode')
        company_valid = StringIO.StringIO(company_valid)
        valid = etree.parse(company_valid)
        if not relaxng.validate(valid):
            raise DropItem




class LagunaKzPipeline(XmlPipeline):

    @check_spider_pipeline
    def process_item(self, item, spider):
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
            m = re.search(u'выход', w)
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

        address_out = oblast + u',город ' + city + ',' + address
        address_out = re.sub('\(|\)', '', address_out)
        address_out = address_out.strip(', ')

        info = self.validate_str(item['info'])
        info = re.sub(u'\”|\"|\«|\»', ' ', info)

        addr_info = address_out + info

        self.counter += 1
        xml_item = etree.SubElement(self.xml, 'company')
        xml_id = etree.SubElement(xml_item, 'company-id')
        xml_id.text = self.company_id(addr_info)

        xml_name = etree.SubElement(xml_item, 'name', lang=u'ru')
        xml_name.text = u"Лагуна"

        xml_address = etree.SubElement(xml_item, 'address', lang=u'ru')
        xml_address.text = address_out

        xml_address_add = etree.SubElement(xml_item,'address-add', lang=u"ru")
        xml_address_add.text = info

        xml_country = etree.SubElement(xml_item, 'country', lang=u'ru')
        xml_country.text = country

        for phone in self.validate_phones(p_str, type):
            xml_phone = etree.SubElement(xml_item, 'phone')
            xml_phone_number = etree.SubElement(xml_phone, 'number')
            xml_phone_number.text = phone.strip()
            xml_phone_type = etree.SubElement(xml_phone, 'type')
            xml_phone_type.text = u'phone'
            xml_phone_ext = etree.SubElement(xml_phone, 'ext')
            xml_phone_info = etree.SubElement(xml_phone, 'info')

        xml_url = etree.SubElement(xml_item, 'url')
        xml_url.text = u"http://www.laguna.by/"

        xml_url_add = etree.SubElement(xml_item, 'add-url')
        xml_url_add.text = url

        if working_time:
            xml_working_time = etree.SubElement(xml_item, 'working-time', lang=u"ru")
            xml_working_time.text = working_time

        xml_rubric = etree.SubElement(xml_item, 'rubric-id')
        xml_rubric.text = u"184107871"

        xml_date = etree.SubElement(xml_item, 'actualization-date')
        xml_date.text = unicode(int(round(time.time() * 1000)))

        company_valid = etree.tostring(xml_item, pretty_print=True, encoding='unicode')
        company_valid = StringIO.StringIO(company_valid)
        valid = etree.parse(company_valid)
        if not relaxng.validate(valid):
            raise DropItem


