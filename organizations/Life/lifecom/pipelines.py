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

BY_CITIES = {
    u"Минская область": [
        u"Березино",
        u"Борисов",
        u"Вилейка",
        u"Воложин",
        u"Дзержинск",
        u"Дружный",  # поселок
        u"Клецк",
        u"Копыль",
        u"Крупки",
        u"Логойск",
        u"Любань",
        u"Лошница",
        u"Молодечно",
        u"Мядель",
        u"Несвиж",
        u"Марьина Горка",
        u"Слуцк",
        u"Смолевичи",
        u"Смиловичи",
        u"Солигорск",
        u"Старые дороги",
        u"Столбцы",
        u"Узда",
        u"Червень",
        u"Жодино",
        u"Нарочь"

    ],
    u"Брестская область": [
        u"Барановичи",
        u"Береза",
        u"Высокое",
        u"Ганцевичи",
        u"Дрогичин",
        u"Жабинка",
        u"Иваново",
        u"Ивацевичи",
        u"Каменец",
        u"Кобрин",
        u"Лунинец",
        u"Ляховичы",
        u"Малорита",
        u"Пинск",
        u"Пружаны",
        u"Столин",
    ],
    u"Витебская область": [
        u"Браслав",
        u"Бешенковичи",
        u"Верхнедвинск",
        u"Глубокое",
        u"Городок",
        u"Докшицы",
        u"Дубровно",
        u"Лепель",
        u"Лиозно",
        u"Миоры",
        u"Новолукомль",
        u"Новополоцк",
        u"Орша",
        u"Полоцк",
        u"Поставы",
        u"Россоны",
        u"Сенно",
        u"Толочин",
        u"Ушачи",
        u"Чашники",
        u"Шарковщина",
        u"Шумилино",
    ],
    u"Гомельская область": [
        u"Брагин",
        u"Буда-Кошелево",
        u"Ветка",
        u"Добруш",
        u"Ельск",
        u"Житковичи",
        u"Жлобин",
        u"Калинковичи",
        u"Корма",
        u"Лельчицы",
        u"Лоев",
        u"Мозырь",
        u"Наровля",
        u"Октябрьский",
        u"Петриков",
        u"Речица",
        u"Рогачев",
        u"Туров",
        u"Светлогорск",
        u"Чечерск",
        u"Хойники",
    ],
    u"Гродненская область": [
        u"Бол.Берестовица",
        u"Волковыск",
        u"Вороново",
        u"Дятлово",
        u"Зельва",
        u"Ивье",
        u"Кореличи",
        u"Лида",
        u"Мосты",
        u"Новогрудок",
        u"Ошмяны",
        u"Островец",
        u"Радунь",  # поселок
        u"Свислочь",
        u"Слоним",
        u"Сморгонь",
        u"Щучин",
    ],
    u"Могилевская область": [
        u"Белыничи",
        u"Березовка",
        u"Бобруйск",
        u"Быхов",
        u"Горки",
        u"Глуск",
        u"Дрибин",
        u"Кировск",
        u"Климовичи",
        u"Кличев",
        u"Костюковичи",
        u"Краснополье",
        u"Кричев",
        u"Круглое",
        u"Мстиславль",
        u"Осиповичи",
        u"Славгород",
        u"Хотимск",
        u"Чаусы",
        u"Чериков",
        u"Шклов",
    ]}


class LifecomPipeline(object):
    counter = 0
    hash_data = []

    def check_hash(self, hash_addr):
        if hash_addr in self.hash_data:
            hash_addr += 1
            hash_addr = self.check_hash(hash_addr)
        return hash_addr

    def company_id(self, address):
        hash_for_address = abs(hash(address))
        hash_for_address = self.check_hash(hash_for_address)
        self.hash_data.append(hash_for_address)
        return unicode(hash_for_address)

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

    def get_region(self, city):
        for k, v in BY_CITIES.iteritems():
            if city in v:
                return k

        return False

    def process_item(self, item, spider):

        name = self.validate_str(item['name'])
        address = self.validate_str(item['address'])

        if name.find(u'Связной') >= 0:
            raise DropItem()

        if name.find(u'Евросеть') >= 0:
            raise DropItem()

        if name.find(u'Клуб') >= 0:
            raise DropItem()

        tsa = self.try_split_addr(address)
        region = self.get_region(self.validate_str(item['city'])) or u""

        if region:
            region += u", "

        if len(tsa) > 1:
            address_to_xml = region + u"город " + self.validate_str(item['city']) + u', ' + tsa[0]
        else:
            address_to_xml = region + u"город " + self.validate_str(item['city']) + u', ' + address

        xml_item = etree.SubElement(self.xml, 'company')

        xml_id = etree.SubElement(xml_item, 'company-id')
        xml_id.text = self.company_id(address_to_xml)

        xml_name = etree.SubElement(xml_item, 'name', lang=u'ru')
        xml_name.text = u'Life:)'

        xml_name = etree.SubElement(xml_item, 'name-other', lang=u'ru')
        xml_name.text = name

        if len(tsa) > 1:
            xml_addr = etree.SubElement(xml_item, 'address', lang=u'ru')
            xml_addr.text = region + u"город " + self.validate_str(item['city']) + u', ' + tsa[0]

            xml_addr_add = etree.SubElement(xml_item, 'address-add', lang=u'ru')
            xml_addr_add.text = tsa[1]
        else:
            xml_addr = etree.SubElement(xml_item, 'address', lang=u'ru')
            xml_addr.text = region + u"город " + self.validate_str(item['city']) + u', ' + address

        xml_country = etree.SubElement(xml_item, 'country', lang=u'ru')
        xml_country.text = u'Беларусь'

        # <phone>
        #     <number>+7 (343) 375-13-99</number>
        #     <ext>555</ext>
        #     <info>секретарь</info>
        #     <type>phone</type>
        # </phone>

        xml_phone_default = etree.SubElement(xml_item, 'phone')
        xml_phone_number = etree.SubElement(xml_phone_default, 'number')
        xml_phone_number.text = u"+375 (25) 909-09-09"
        xml_phone_type = etree.SubElement(xml_phone_default, 'type')
        xml_phone_type.text = u'phone'
        xml_phone_ext = etree.SubElement(xml_phone_default, 'ext')
        xml_phone_info = etree.SubElement(xml_phone_default, 'info')

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

        working_time = zip(item['days'], item['times'])

        work_str = ''
        for k, v in working_time:
            if u'выходной' not in v.lower() and u'закрыто' not in v.lower():
                work_str += k + ':' + v.replace('*', '') + ' , '

        # times_set = []
        # for t in item['times']:
        #     if t not in times_set:
        #         times_set.append(t)
        #
        # in_map = {}
        # for t in times_set:
        #     in_map[t] = list()
        #     for k,v in working_time:
        #         if t == v:
        #             in_map[t].append(k)
        #
        # work_str = ''
        # for t in times_set:
        #     if u'выходной' not in t.lower():
        #         if len(in_map[t]) > 1:
        #             work_str += ''.join(in_map[t][:1]) +'-'+''.join(in_map[t][-1:]) + ':' + t + ' , '
        #         else:
        #             work_str += ''.join(in_map[t][0]) + ':' + t + ' , '

        xml_time.text = work_str[:-3]

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
