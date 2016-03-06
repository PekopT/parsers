# -*- coding: utf-8 -*-
import time
import re
from codecs import getwriter
from sys import stdout
from lxml import etree
from scrapy.exceptions import DropItem

from utils import BY_CODES, BY_CITIES

sout = getwriter("utf8")(stdout)


class OhranagovbyPipeline(object):
    def __init__(self):
        self.count_item = 0
        self.ns = {"xi": 'http://www.w3.org/2001/XInclude'}
        self.xml = etree.Element('companies', version='2.1', nsmap=self.ns)

    def company_id(self):
        return u'0000' + unicode(self.count_item)

    def get_city(self, value):
        city_ag = re.search(u'аг\.\s*[А-Яа-я\-]+', value)
        city_only = re.search(u'г\.\s*[А-Яа-я\-]+', value)
        city_with_p = re.search(u'г\.п\.\s*[А-Яа-я\-]+', value)
        village = re.search(u'д\.\s*[А-Яа-я\-]+', value)
        if city_with_p:
            result = city_with_p.group(0).strip()
            if value.find(result) == 0:
                poselok = re.sub(u'г\.п\.\s*', u'', result)
                region = self.get_region(poselok) or u""
                address_sub = re.sub(result, '', value)
                city = region + u"поселок " + poselok + address_sub
            else:
                city = value
        elif city_ag:
            result = city_ag.group(0).strip()
            city = re.sub(u'аг\.\s*', u'АГ', result)
        elif city_only:
            result = city_only.group(0).strip()
            if value.find(result) == 0:
                city = re.sub(u'г\.\s*', u'', result)
                region = self.get_region(city) or u""
                address_sub = re.sub(result, '', value)
                city = region + u"город " + city + address_sub
            else:
                city = value
        elif village:
            result = village.group(0).strip()
            if value.find(result) == 0:
                vil = re.sub(u'д\.\s*', u'', result)
                region = self.get_region(vil) or u""
                address_sub = re.sub(result, '', value)
                city = region + u"город " + vil + address_sub
            else:
                city = value

        else:
            city = u'not found' + value

        return city

    def get_region(self, city):
        if u"Старые" in city:
            city = u"Старые Дороги"
        elif u"Марьина" in city:
            city = u"Марьина Горка"

        for k, v in BY_CITIES.iteritems():
            if city in v:
                return k + u","
        return False

    def formattion_address(self, value):
        return value

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

    def formatter_workin_time(self, value):
        if type(value) == list:
            val = u""
            for v in value:
                if v.strip():
                    val_temp = v.strip()
                    if not re.search(u"вихід", val_temp):
                        val += u"," + v.strip()

            if val is None:
                return u""
        else:
            val = value

        return val.strip()

    def tel_format(self, phones, phone_code):
        phns = []
        if len(phones) == 1 and len(phones[0]) >15:
            phones = [phones[0][0:11], phones[0][11:]]
        for p in phones:
            p = re.sub(u'^80|^375', u'', p)
            if phone_code:
                phone_code = re.sub(u'^0', u'', phone_code)
            else:
                for c in BY_CODES:
                    if p.find(c) == 0:
                        phone_code = c
                        break
            if len(p) < 8:
                p = u'+375 (' + phone_code + u') ' + p
                phns.append(p)
            else:
                p = re.sub('^80', '', p)
                for c in BY_CODES:
                    if p.find(c) == 0:
                        phns.append(u'+375 (' + c + u') ' + re.sub(u"^%s" % c, u'', p))
                        phone_code = c
                        break

        return phns

    def tel_test(self, value):
        phones = []
        if not value:
            return []
        for phone in value:
            phone = self.delete_tags(phone)
            phone_check = re.sub(u'\D', '', phone).strip()
            if phone_check:
                if ';' in phone:
                    phns = phone.split(';')
                elif ',' in phone:
                    phns = phone.split(',')
                elif '\n' in phone:
                    phns = phone.split('\n')
                else:
                    phns = phone.split(',')

                for ph in phns:
                    if ph.strip():
                        ph = ph.strip()
                        ph = re.sub('\D', '', ph)
                        phones.append(ph)

        return phones

    def validate_phones(self, phone):
        phones = []
        if not phone:
            return []
        if ';' in phone:
            phns = phone.split(';')
        else:
            phns = phone.split(',')

        for ph in phns:
            if ph.strip():
                ph = ph.strip()
                # phone = re.sub('\D', '', ph)
                phones.append(u"+380 " + phone)

        return phones

    def delete_tags(self, value):
        pattern = u'\<[^>]*\>'
        value = re.sub(pattern, '', value)
        value = re.sub(u'&#13;|&lt;|&gt;|<|>|\/li|\r', '', value)
        value = re.sub(u'td|span|\/|br', '', value)
        return value

    def delete_brackets(self, value):
        pattern = u'\(.*\)'
        value = re.sub(pattern, '', value)
        return value

    def formatter_name(self, value, url):
        if url != "http://ohrana.gov.by/wp/about-department/territorial-authorities/":
            value = u"Департамент Охраны МВД РБ " + value
        return value

    def process_item(self, item, spider):
        name = self.delete_tags(self.validate_str(item['name']))
        name = self.delete_brackets(name)
        name = self.formatter_name(name, item['url'])

        address = self.validate_str(item['address'])
        address = self.delete_tags(address)

        address = re.sub(u'\d{6}', '', address).strip(';, .')
        address = re.sub(u'адрес:|Республика Беларусь', '', address).strip(';, .')
        pos_addr = address.find(u'г. Клецк')
        if pos_addr > 0:
            address = address[pos_addr:]
        address = self.delete_brackets(address)

        mp = re.search(u"г\.п\.\s*[А-Яа-я-]+", address)
        mc = re.search(u"г\.\s*[А-Яа-я-]+", address)
        if mp:
            city = mp.group(0)
            city = re.sub(u"г\.п\.\s*", u'', city)
        elif mc:
            city = mc.group(0)
            city = re.sub(u"г\.\s*", u'', city)
        else:
            city = u""

        if city:
            region = self.get_region(city) or ""

        address = region + re.sub(u'г\.\s*', u'город ', address)
        phones = self.tel_test(item['phone'])
        phone_code = item['phone_code']

        self.count_item += 1
        xml_item = etree.SubElement(self.xml, 'company')

        xml_id = etree.SubElement(xml_item, 'company-id')
        xml_id.text = self.company_id()

        xml_name = etree.SubElement(xml_item, 'name', lang=u'ru')
        xml_name.text = name

        xml_address = etree.SubElement(xml_item, 'address',lang=u'ru')
        xml_address.text = address

        phones_itogo = self.tel_test(item['phone'])
        phones_itogo = self.tel_format(phones_itogo, phone_code)
        for phone in phones_itogo:
            vp = re.search(u"\(\)", phone)
            if not vp:
                xml_phone = etree.SubElement(xml_item, 'phone')
                xml_phone_number = etree.SubElement(xml_phone, 'number')
                xml_phone_number.text = phone
                xml_phone_type = etree.SubElement(xml_phone, 'type')
                xml_phone_type.text = u'phone'
                xml_phone_ext = etree.SubElement(xml_phone, 'ext')
                xml_phone_info = etree.SubElement(xml_phone, 'info')

        xml_url = etree.SubElement(xml_item, 'url')
        xml_url.text = u"http://ohrana.gov.by"

        xml_url_add = etree.SubElement(xml_item, 'add-url')
        xml_url_add.text = item['url']

        xml_rubric = etree.SubElement(xml_item, 'rubric-id')
        xml_rubric.text = u"52444182335"

        xml_date = etree.SubElement(xml_item, 'actualization-date')
        xml_date.text = unicode(int(round(time.time() * 1000)))

    def close_spider(self, spider):
        doc = etree.tostring(self.xml, pretty_print=True, encoding='unicode')
        sout.write('<?xml version="1.0" encoding="UTF-8" ?>' + '\n')
        sout.write(doc)
