# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import time
import re
import StringIO
from codecs import getwriter
from sys import stdout
from lxml import etree

from scrapy.exceptions import DropItem
from schema_org import SCHEMA_ORG

sout = getwriter("utf8")(stdout)

relaxng_doc = etree.parse(SCHEMA_ORG)
relaxng = etree.RelaxNG(relaxng_doc)

BY_TYL_CODES = [unicode(x) for x in (
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
    2248,
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
    2131,
    2130,
    2132,
    2133,
    2135,
    2136,
    225,
    17,
    25,
    163,
    212,
    214,
    215,
    216,
    152,
    2139,
    154,
    2138,
    236,
    29,
    44,



)]

BY_CITIES = {
    u"Минская область": [
        u"Березино",
        u"Борисов",
        u"Вилейка",
        u"Вишневка",
        u"Воложин",
        u"Дзержинск",
        u"Красное",
        u"Ивенец",
        u"Клецк",
        u"Копыль",
        u"Крупки",
        u"Логойск",
        u"Любань",
        u"Заславль",
        u"Молодечно",
        u"Малявка",
        u"Мядель",
        u"Несвиж",
        u"Марьина Горка",
        u"Слуцк",
        u"Смолевичи",
        u"Смиловичи",
        u"Солигорск",
        u"Старые Дороги",
        u"Столбцы",
        u"Фаниполь",
        u"Узда",
        u"Червень",
        u"Жодино",
        u"Озерцы",
        u"Поречье",
        u"Заболоть",
        u"Новоселки",
        u"Хозянинки",
        u"Озерцо",


    ],
    u"Брестская область": [
        u"Барановичи",
        u"Брест",
        u"Береза",
        u"Ганцевичи",
        u"Видомля",
        u"Дрогичин",
        u"Дивин",
        u"Жабинка",
        u"Иваново",
        u"Ивацевичи",
        u"Каменец",
        u"Каменюки",
        u"Кобрин",
        u"Лунинец",
        u"Ляховичы",
        u"Малорита",
        u"Пинск",
        u"Пружаны",
        u"Столин",
        u"Невель",
        u"Сосновка",
        u"Бытень",
        u"Углы",
        u"Новоселки",
        u"Березовичи",
        u"Поречье",
        u"Посеничи",
        u"Томашовка",
        u"Мотоль",
    ],
    u"Витебская область": [
        u"Браслав",
        u"Бешенковичи",
        u"Бегомль",
        u"Верхнедвинск",
        u"Ветрино",
        u"Воропаево",
        u"Видзы",
        u"Глубокое",
        u"Городок",
        u"Докшицы",
        u"Дубровно",
        u"Друя",
        u"Езерище",
        u"Красносельцы",
        u"Фролковичи",
        u"Лепель",
        u"Лиозно",
        u"Лукомль",
        u"Лынтупы",
        u"Миоры",
        u"Новополоцк",
        u"Орша",
        u"Освея",
        u"Остевичи",
        u"Полоцк",
        u"Подсвилье",
        u"Поставы",
        u"Россоны",
        u"Сенно",
        u"Сураж",
        u"Толочин",
        u"Тросно",
        u"Чернещино",
        u"Ушачи",
        u"Чашники",
        u"Шарковщина",
        u"Шумилино",
        u"Вороны",
        u"Озеры",
        u"Сосновка",
        u"Волколата",
        u"Крулевщина",
        u"Азино",
        u"Новоселки",
        u"Сорочино",
        u"Муравничи",
    ],
    u"Гомельская область": [
        u"Брагин",
        u"Буда-Кошелево",
        u"Урицкое",
        u"Ветка",
        u"Добруш",
        u"Ельск",
        u"Житковичи",
        u"Жлобин",
        u"Калинковичи",
        u"Корма",
        u"Копаткевичи",
        u"Лельчицы",
        u"Лоев",
        u"Мозырь",
        u"Наровля",
        u"Октябрьский",
        u"Петриков",
        u"Речица",
        u"Рогачев",
        u"Светлогорск",
        u"Чечерск",
        u"Хойники",
        u"Поречье",
        u"Добрынский",
        u"Защебье",
        u"Довск",
        u"Лясковичи",
        u"Новая Гута",
    ],
    u"Гродненская область": [
        u"Бол.Берестовица",
        u"Березовка",
        u"Будёновка",
        u"Волковыск",
        u"Вороново",
        u"Ворона",
        u"Дятлово",
        u"Зельва",
        u"Ивье",
        u"Красносельский",
        u"Каменный лог",
        u"Кореличи",
        u"Козловщина",
        u"Лида",
        u"Мосты",
        u"Муравщизна",
        u"Новогрудок",
        u"Новая Стража",
        u"Новоельня",
        u"Ошмяны",
        u"Островец",
        u"Острино",
        u"Островля",
        u"Порозово",
        u"Скидель",
        u"Радунь",
        u"Свислочь",
        u"Слоним",
        u"Сморгонь",
        u"Чемеры",
        u"Щучин",
        u"Заболоть",
        u"Озеры",
        u"Михалишки",
        u"Новоселки",
        u"Поречье",
        u"Сосновка",
    ],
    u"Могилевская область": [
        u"Белыничи",
        u"Бобруйск",
        u"Бол. Бортники",
        u"Быхов",
        u"Горки",
        u"Глуск",
        u"Дрибин",
        u"Елизово",
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
        u"Новоселки",
        u"Сычково",
        u"Чечевичи",
        u"Белица",
        u"Звенчатка",
        u"Ходосы",
        u"Ректа",
        u"Достижение",
    ]}


class BelorusneftPipeline(object):
    def __init__(self):
        self.count_item = 0
        self.ns = {"xi": 'http://www.w3.org/2001/XInclude'}
        self.xml = etree.Element('companies', version='2.1', nsmap=self.ns)

    def company_id(self):
        return u'0009' + unicode(self.count_item)


    def get_city(self, value):
        city_ag = re.search(u'аг\.\s*[А-Яа-я\-]+', value)
        city_only = re.search(u'г\.\s*[А-Яа-я\-]+', value)
        city_with_p = re.search(u'г\.п\.\s*[А-Яа-я\-]+', value)
        village = re.search(u'д\.\s*[А-Яа-яё\-]+', value)
        if city_with_p:
            result = city_with_p.group(0).strip()
            if value.find(result) == 0:
                poselok = re.sub(u'г\.п\.\s*', u'', result)
                region = self.get_region(poselok) or u""
                address_sub = re.sub(result,'',value)
                city = region + u"поселок " + poselok + address_sub
            else:
                city = value
        elif city_ag:
            result = city_ag.group(0).strip()
            city = re.sub(u'аг\.\s*', u'', result)
            if city == u"Новая":
                    city = u"Новая Гута"
                    result = u"аг. Новая Гута"
            region = self.get_region(city) or u""
            pos = value.find(result) + len(result)
            address_sub = value[pos:]
            city = region + u"аг " + city  + address_sub
        elif city_only:
            result = city_only.group(0).strip()
            if value.find(result) == 0:
                city = re.sub(u'г\.\s*', u'', result)
                region = self.get_region(city) or u""
                address_sub = re.sub(result,'',value)
                city = region + u"город " + city + address_sub
            else:
                city = value
        elif village:
            result = village.group(0).strip()
            if value.find(result) == 0:
                vil = re.sub(u'д\.\s*', u'', result)
                vil = vil.strip()
                if vil == u"Новая":
                    vil = u"Новая Стража"
                    result = u"д. Новая Стража"
                elif vil == u"Бол":
                    vil = u"Бол. Бортники"
                    result = u"д. Бол. Бортники"
                elif vil == u"Каменный":
                    vil = u"Каменный лог"
                    result = u"д. Каменный лог"
                else:
                    pass
                address_sub = re.sub(result,'',value)
                region = self.get_region(vil) or u""

                city = region + u"деревня " + vil + address_sub
            else:
                city = value

        else:
            city = value

        return city

    def get_region(self,city):
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

    def validate_phones(self, phone):
        phones = []
        if not phone:
            return []
        phone = re.sub('\(', ',(', phone)
        if ';' in phone:
            phns = phone.split(';')
        else:
            phns = phone.split(',')

        for ph in phns:
            if ph.strip():

                ph = ph.strip()
                ph = re.sub('^\+375','',ph)
                ph = re.sub('\D', '', ph)
                ph = re.sub('^8','',ph)
                ph = re.sub('^0','',ph)
                if len(ph)>9:
                    ph = re.sub('^0','',ph)

                for code in BY_TYL_CODES:
                    if ph.find(code) == 0:
                        phones.append(u"+380" + u" (" + code + u") " + re.sub("^%s" % code, '', ph))
                        break

        return phones

    def process_item(self, item, spider):
        address = item['address']
        phones = item['phone']
        fuels = item['fuels']

        if not phones:
            raise DropItem

        self.count_item += 1
        xml_item = etree.SubElement(self.xml, 'company')
        xml_id = etree.SubElement(xml_item, 'company-id')
        xml_id.text = self.company_id()
        # xml_address_raw = etree.SubElement(xml_item, 'address_raw', lang=u'ua')
        # xml_address_raw.text = address

        xml_address = etree.SubElement(xml_item, 'address', lang=u'ua')
        xml_address.text = self.get_city(address)

        for phone in self.validate_phones(phones):
            xml_phone = etree.SubElement(xml_item, 'phone')
            xml_phone_number = etree.SubElement(xml_phone, 'number')
            xml_phone_number.text = phone
            xml_phone_type = etree.SubElement(xml_phone, 'type')
            xml_phone_type.text = u'phone'
            xml_phone_ext = etree.SubElement(xml_phone, 'ext')
            xml_phone_info = etree.SubElement(xml_phone, 'info')

        xml_rubric = etree.SubElement(xml_item, 'rubric-id')
        xml_rubric.text = u"184105274"

        if re.search(u"title='Газ'", fuels):
            xml_rubric2 = etree.SubElement(xml_item, 'rubric-id')
            xml_rubric2.text = u"184105272"

        xml_date = etree.SubElement(xml_item, 'actualization-date')
        xml_date.text = unicode(int(round(time.time() * 1000)))

        company_valid = etree.tostring(xml_item, pretty_print=True, encoding='unicode')
        company_valid = StringIO.StringIO(company_valid)
        valid = etree.parse(company_valid)
        if not relaxng.validate(valid):
            raise DropItem

    def close_spider(self, spider):
        doc = etree.tostring(self.xml, pretty_print=True, encoding='unicode')
        sout.write('<?xml version="1.0" encoding="UTF-8" ?>' + '\n')
        sout.write(doc)
