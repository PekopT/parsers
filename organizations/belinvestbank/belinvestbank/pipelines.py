# -*- coding: utf-8 -*-

from sys import stdout
import time

import re
from belinvestbank.utils import check_spider_pipeline, check_spider_close
from lxml import etree
from codecs import getwriter

sout = getwriter("utf8")(stdout)

BY_TYL_CODES = [unicode(x) for x in (
    17,
    25,
    29,
    163,
    2232,
    1643,
    1715,
    1511,
    2251,
    1777,
    2344,
    162,
    2336,
    2231,
    2330,
    1771,
    1512,
    1772,
    1594,
    1646,
    2230,
    232,
    2233,
    1522,
    1716,
    2333,
    1644,
    1563,
    2354,
    1641,
    2353,
    2334,
    1775,
    1564,
    1652,
    1645,
    1595,
    2345,
    1631,
    2237,
    1793,
    2244,
    2236,
    1642,
    1719,
    1596,
    2337,
    2245,
    2238,
    2241,
    2234,
    1796,
    2356,
    1561,
    1774,
    2347,
    1647,
    1794,
    1633,
    1651,
    1713,
    2222,
    222,
    2351,
    1773,
    1515,
    2240,
    1797,
    2355,
    1797,
    1770,
    1597,
    2357,
    2235,
    1591,
    1593,
    2350,
    1653,
    1632,
    1713,
    2340,
    2339,
    2342,
    1513,
    2246,
    1562,
    1795,
    1776,
    1592,
    1710,
    1792,
    1717,
    1655,
    1718,
    2346,
    2247,
    2242,
    1714,
    2243,
    1732,
    2332,
    2239,
    1514,
    225
)]


class XmlPipeline(object):
    counter = 0

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

        return val.strip()

    def company_id(self):
        return u'0001' + unicode(self.counter)

    def __init__(self):
        self.ns = {"xi": 'http://www.w3.org/2001/XInclude'}
        self.xml = etree.Element('companies', version='2.1', nsmap=self.ns)

    @check_spider_close
    def close_spider(self, spider):
        doc = etree.tostring(self.xml, pretty_print=True, encoding='unicode')
        sout.write('<?xml version="1.0" encoding="UTF-8" ?>' + '\n')
        sout.write(doc)


class BelinvestbankAtmPipeline(XmlPipeline):
    @check_spider_pipeline
    def process_item(self, item, spider):
        # <companies xmlns:xi="http://www.w3.org/2001/XInclude" version="2.1"></companies>
        xml_item = etree.SubElement(self.xml, 'company')

        xml_id = etree.SubElement(xml_item, 'company-id')
        xml_id.text = self.company_id()

        xml_name = etree.SubElement(xml_item, 'name')
        xml_name.text = u'Белинвестбанк, банкомат'

        xml_addr = etree.SubElement(xml_item, 'address', lang=u'ru')
        addr = re.sub(u'Банкомат ([№\d ,]+)?', '', item['name']).replace('  ', ' ')

        if addr.find(u"Минск ") != -1 or addr.find(u"Минск,") != -1:
            xml_addr.text = addr
        else:
            if xml_addr.find(u'г.') != -1:
                xml_addr.text = item['region'].replace(u'Минск и ', '') + u', ' + addr
            else:
                xml_addr.text = item['region'] + u', ' + addr

        xml_addr_add = etree.SubElement(xml_item, 'address-add', lang=u'ru')
        xml_addr_add.text = self.validate_str(item['add_address']).rstrip(',) ').lstrip(',( ')

        xml_country = etree.SubElement(xml_item, 'country', lang=u'ru')
        xml_country.text = u'Беларусь'

        xml_phone = etree.SubElement(xml_item, 'phone')
        xml_phone_number = etree.SubElement(xml_phone, 'number')
        xml_phone_number.text = u"+375 (17) 239-02-39"
        xml_phone_type = etree.SubElement(xml_phone, 'type')
        xml_phone_type.text = u'phone'
        xml_phone_ext = etree.SubElement(xml_phone, 'ext')
        xml_phone_info = etree.SubElement(xml_phone, 'info')

        # url
        xml_url = etree.SubElement(xml_item, 'url')
        xml_url.text = u'http://www.belinvestbank.by'

        # add-url
        xml_url = etree.SubElement(xml_item, 'add-url')
        xml_url.text = item['url']

        # working-time
        xml_country = etree.SubElement(xml_item, 'working-time', lang=u'ru')
        xml_country.text = item['time']

        # <rubric-id>184106414</rubric-id>
        xml_rubric = etree.SubElement(xml_item, 'rubric-id')
        xml_rubric.text = u"184105402"  # Банкомат (184105402)

        # <actualization-date>1305705951000</actualization-date>
        xml_date = etree.SubElement(xml_item, 'actualization-date')
        xml_date.text = unicode(int(round(time.time() * 1000)))

        for cur in item['curr']:
            # <enum-value name="currency_atm">atm_usd</enum-value>
            curr_text = u'atm_' + cur
            curr = etree.SubElement(xml_item, 'feature-enum-multiple', name='currency_atm', value=curr_text)

        if item['accept']:
            # <known-boolean name="cash_to_card"/>
            etree.SubElement(xml_item, 'feature-boolean', name='cash_to_card', value='1')

        self.counter += 1


class BelinvestbankInfoPipeline(XmlPipeline):
    @check_spider_pipeline
    def process_item(self, item, spider):
        # <companies xmlns:xi="http://www.w3.org/2001/XInclude" version="2.1"></companies>
        xml_item = etree.SubElement(self.xml, 'company')

        xml_id = etree.SubElement(xml_item, 'company-id')
        xml_id.text = self.company_id()  # TODO

        xml_name = etree.SubElement(xml_item, 'name')
        xml_name.text = u'Белинвестбанк, инфокиоск'

        xml_addr = etree.SubElement(xml_item, 'address', lang=u'ru')
        addr = re.sub(u'Инфокиоск ([№\d ,]+)?', '', item['name']).replace('  ', ' ')

        if addr.find(u"Минск ") != -1 or addr.find(u"Минск,") != -1:
            xml_addr.text = addr
        else:
            if xml_addr.find(u'г.') != -1:
                xml_addr.text = item['region'].replace(u'Минск и ', '') + u', ' + addr
            else:
                xml_addr.text = item['region'] + u', ' + addr

        xml_addr_add = etree.SubElement(xml_item, 'address-add', lang=u'ru')
        xml_addr_add.text = self.validate_str(item['add_address']).rstrip(',')

        xml_country = etree.SubElement(xml_item, 'country', lang=u'ru')
        xml_country.text = u'Беларусь'

        xml_phone = etree.SubElement(xml_item, 'phone')
        xml_phone_number = etree.SubElement(xml_phone, 'number')
        xml_phone_number.text = u"+375 (17) 239-02-39"
        xml_phone_type = etree.SubElement(xml_phone, 'type')
        xml_phone_type.text = u'phone'
        xml_phone_ext = etree.SubElement(xml_phone, 'ext')
        xml_phone_info = etree.SubElement(xml_phone, 'info')

        # url
        xml_url = etree.SubElement(xml_item, 'url')
        xml_url.text = u'http://www.belinvestbank.by'

        # url
        xml_url = etree.SubElement(xml_item, 'add-url')
        xml_url.text = item['url']

        # working-time
        xml_country = etree.SubElement(xml_item, 'working-time', lang=u'ru')
        xml_country.text = item['time']

        # <rubric-id>184106414</rubric-id>
        xml_rubric = etree.SubElement(xml_item, 'rubric-id')
        xml_rubric.text = u"31320523497"  # Инфокиоск (31320523497)

        # <actualization-date>1305705951000</actualization-date>
        xml_date = etree.SubElement(xml_item, 'actualization-date')
        xml_date.text = unicode(int(round(time.time() * 1000)))

        # for cur in item['curr']:
            # <enum-value name="currency_atm">atm_usd</enum-value>
            # curr = etree.SubElement(xml_item, 'feature-enum-multiple', name='currency_atm')
            # curr.text = u'atm_' + cur

        self.counter += 1


class BelinvestbankOfficePipeline(XmlPipeline):
    def validate_tel(self, value):
        phones = []
        if not value:
            return phones

        for tels in value:
            phns = tels.split(',')
            for phone in phns:
                number = re.sub("\D", '', phone).strip()
                number = re.sub("^80", '', number)
                for code in BY_TYL_CODES:
                    if number.find(code) == 0:
                        phones.append(u"+375" + u" (" + code + u") " + re.sub("^%s" % code, '', number))
                        break
        return phones

    @check_spider_pipeline
    def process_item(self, item, spider):

        if self.counter == 198:
            spider.log(item)
        xml_item = etree.SubElement(self.xml, 'company')

        xml_id = etree.SubElement(xml_item, 'company-id')
        xml_id.text = self.company_id()
        self.counter += 1

        xml_name = etree.SubElement(xml_item, 'name')
        xml_name.text = u'Белинвестбанк, ' + item['name']

        xml_addr = etree.SubElement(xml_item, 'address', lang=u'ru')
        addr = item['address'].strip().rstrip(',')
        add_addr = False
        try_split = addr.split('(')
        if len(try_split) > 1:
            addr = try_split[0].strip().rstrip(',')
            add_addr = try_split[1].strip().rstrip(',').rstrip(')')

        if addr.find(u"Минск ") != -1 or addr.find(u"Минск,") != -1:
            xml_addr.text = addr
        else:
            if xml_addr.find(u'г.') != -1:
                xml_addr.text = item['region'].replace(u'Минск и ', '') + u', ' + addr
            else:
                xml_addr.text = item['region'] + u', ' + addr

        if add_addr:
            xml_addr_add = etree.SubElement(xml_item, 'address-add', lang=u'ru')
            xml_addr_add.text = add_addr

        xml_country = etree.SubElement(xml_item, 'country', lang=u'ru')
        xml_country.text = u'Беларусь'

        xml_phone = etree.SubElement(xml_item, 'phone')
        xml_phone_number = etree.SubElement(xml_phone, 'number')
        xml_phone_number.text = u"+375 (17) 239-02-39"
        xml_phone_type = etree.SubElement(xml_phone, 'type')
        xml_phone_type.text = u'phone'
        xml_phone_ext = etree.SubElement(xml_phone, 'ext')
        xml_phone_info = etree.SubElement(xml_phone, 'info')

        for phone in self.validate_tel(item['phones']):
            xml_phone = etree.SubElement(xml_item, 'phone')
            xml_phone_number = etree.SubElement(xml_phone, 'number')
            xml_phone_number.text = phone
            xml_phone_type = etree.SubElement(xml_phone, 'type')
            xml_phone_type.text = u'phone'
            xml_phone_ext = etree.SubElement(xml_phone, 'ext')
            xml_phone_info = etree.SubElement(xml_phone, 'info')

        # url
        xml_url = etree.SubElement(xml_item, 'url')
        xml_url.text = u'http://www.belinvestbank.by'

        # add-url
        xml_url = etree.SubElement(xml_item, 'add-url')
        xml_url.text = item['url']

        # working-time
        xml_country = etree.SubElement(xml_item, 'working-time', lang=u'ru')
        xml_country.text = item['time']

        # <rubric-id>184106414</rubric-id>
        xml_rubric = etree.SubElement(xml_item, 'rubric-id')
        xml_rubric.text = u"184105398"  # Банк (31320523497)
        xml_rubric2 = etree.SubElement(xml_item, 'rubric-id')
        xml_rubric2.text = u"184105406"  # Обмен валют (31320523497)

        # <actualization-date>1305705951000</actualization-date>
        xml_date = etree.SubElement(xml_item, 'actualization-date')
        xml_date.text = unicode(int(round(time.time() * 1000)))
