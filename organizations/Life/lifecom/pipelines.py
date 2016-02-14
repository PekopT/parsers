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

BY_TYL_CODES = [unicode(x) for x in (
    17,
    25,
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
    1514
)]


class LifecomPipeline(object):
    counter = 0

    def company_id(self):
        return u'0004' + unicode(self.counter)

    def __init__(self):
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

    def validate_tel(self, value):
        phones = []
        if not value:
            return phones

        for tels in value:
            phns = tels.split(',')
            for phone in phns:
                number = re.sub("\D", '', phone).strip()
                number = re.sub("^375", '', number)
                for code in BY_TYL_CODES:
                    if number.find(code) == 0:
                        phones.append(u"+375" + u" (" + code + u") " + re.sub("^%s" % code, '', number))
                        break
        return phones

    def try_split_addr(self, addr):
        dels = [u'ТЦ', u'ТРЦ', u'(']
        pos = {}
        for deli in dels:
            if addr.find(deli) != -1:
                pos[addr.find(deli)] = deli

        if pos:
            key = min(pos.keys())
            value = pos.get(key)

            splt = [x.rstrip(',) ').lstrip(',( ') for x in addr.split(value, 1)]
            if len(splt) > 1 and value != u'(':
                splt[1] = value + u" " + splt[1]

            return splt
        return [addr, ]

    def get_borders(self, days):
        ethalon = [u'Пн', u'Вт', u'Ср', u'Чт', u'Пт', u'Сб', u'Вс']
        sortd = sorted(days, key=lambda x: ethalon.index(x))
        return list(set([sortd[0], sortd[-1]]))

    def process_item(self, item, spider):

        name = self.validate_str(item['name'])
        address = self.validate_str(item['address'])

        if name.find(u'Связной') >= 0:
            raise DropItem()

        if name.find(u'Евросеть') >= 0:
            raise DropItem()

        xml_item = etree.SubElement(self.xml, 'company')

        xml_id = etree.SubElement(xml_item, 'company-id')
        xml_id.text = self.company_id()  # TODO

        xml_name = etree.SubElement(xml_item, 'name', lang=u'ru')
        xml_name.text = u'Life:)'

        xml_name = etree.SubElement(xml_item, 'name-other', lang=u'ru')
        xml_name.text = name

        tsa = self.try_split_addr(address)
        if len(tsa) > 1:
            xml_addr = etree.SubElement(xml_item, 'address', lang=u'ru')
            xml_addr.text = u"город " + self.validate_str(item['city']) + u', ' + tsa[0]

            xml_addr_add = etree.SubElement(xml_item, 'address-add', lang=u'ru')
            xml_addr_add.text = tsa[1]
        else:
            xml_addr = etree.SubElement(xml_item, 'address', lang=u'ru')
            xml_addr.text = u"город " + self.validate_str(item['city']) + u', ' + address

        xml_country = etree.SubElement(xml_item, 'country', lang=u'ru')
        xml_country.text = u'Беларусь'

        # <phone>
        #     <number>+7 (343) 375-13-99</number>
        #     <ext>555</ext>
        #     <info>секретарь</info>
        #     <type>phone</type>
        # </phone>
        for phone in self.validate_tel(item['phone']):
            xml_phone = etree.SubElement(xml_item, 'phone')
            xml_phone_number = etree.SubElement(xml_phone, 'number')
            xml_phone_number.text = phone
            xml_phone_type = etree.SubElement(xml_phone, 'type')
            xml_phone_type.text = u'phone'
            xml_phone_ext = etree.SubElement(xml_phone, 'ext')
            xml_phone_info = etree.SubElement(xml_phone, 'info')

        # url
        xml_url = etree.SubElement(xml_item, 'url')
        xml_url.text = u'http://www.life.com.by'

        # add-url
        xml_url = etree.SubElement(xml_item, 'add-url')
        xml_url.text = item['url']

        # working-time
        xml_time = etree.SubElement(xml_item, 'working-time', lang=u'ru')

        inv_map = {}
        for k, v in item['time'].iteritems():
            inv_map[v] = inv_map.get(v, [])
            inv_map[v].append(k)
        work_time = []
        for t, d in inv_map.iteritems():
            work_time.append(u"-".join(self.get_borders(d)) + u": " + t.strip(' '))
        xml_time.text = u', '.join(work_time)

        # <rubric-id>184106414</rubric-id>
        xml_rubric = etree.SubElement(xml_item, 'rubric-id')
        xml_rubric.text = u"184107789"  # Салон связи(184107789)
        xml_rubric2 = etree.SubElement(xml_item, 'rubric-id')
        xml_rubric2.text = u"184107783"  # Оператор сотовой связи(184107783)

        # <actualization-date>1305705951000</actualization-date>
        xml_date = etree.SubElement(xml_item, 'actualization-date')
        xml_date.text = unicode(int(round(time.time() * 1000)))

        self.counter += 1

    def close_spider(self, spider):
        doc = etree.tostring(self.xml, pretty_print=True, encoding='unicode')
        sout.write('<?xml version="1.0" encoding="UTF-8" ?>' + '\n')
        sout.write(doc)
