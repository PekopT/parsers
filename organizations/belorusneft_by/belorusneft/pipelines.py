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
from utils import BY_CITIES, BY_DISTRICT, BY_TYL_CODES, SERVICES, FUELS, ADDITIONAL, FUEL_CARDS, CREDIT_CARD

sout = getwriter("utf8")(stdout)

relaxng_doc = etree.parse(SCHEMA_ORG)
relaxng = etree.RelaxNG(relaxng_doc)


class BelorusneftPipeline(object):

    def __init__(self):
        self.count_item = 0
        self.ns = {"xi": 'http://www.w3.org/2001/XInclude'}
        self.xml = etree.Element('companies', version='2.1', nsmap=self.ns)

    def company_id(self, value):
        str_for_hash = value
        hash_for_address = abs(hash(str_for_hash))
        return unicode(hash_for_address)


    def get_result_city(self, value):
        m = re.search(u'[А-Яа-яё\-]+\s+р\-н', value)
        city_res = value
        if m:
            res = m.group(0).strip()
            if value.find(res) == 0:
                district = re.sub(u'р\-н', u'', res).strip()
                region = self.get_region_district(district) or u""
                city_res = region + value

        return city_res


    def get_result_cc(self, value):
        m = re.search(u'[А-Яа-яё\-]+\s+с\/с', value)
        city_res = value
        if m:
            res = m.group(0).strip()
            if value.find(res) == 0:
                district = re.sub(u'с\/с', u'', res).strip()
                region = self.get_region(district) or u""
                city_res =region + value
        return city_res

    def get_city(self, value):
        value = re.sub(u"(c|с)\/(с|c)",u"с/с", value)
        value = value.replace(u'с-с',u'с/с')
        city_ag = re.search(u'аг\.\s*[А-Яа-я\-]+', value)
        city_only = re.search(u'г\.\s*[А-Яа-я\-]+', value)
        city_with_p = re.search(u'г\.\s?п\.\s*[А-Яа-я\-]+', value)
        village = re.search(u'д\.\s*[А-Яа-яё\-]+', value)
        if city_with_p:
            result = city_with_p.group(0).strip()
            if value.find(result) == 0:
                poselok = re.sub(u'г\.\s?п\.\s*', u'', result)
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
            cc = re.search(u'[А-Яа-яё\-]+\s+с\/с', value)
            np = re.search(u'н\.п\.\s*[А-Яа-яё\-]+', value)
            p_only = re.search(u'п\.\s*[А-Яа-яё\-]+', value)
            city_res = u''

            if cc:
                res = cc.group(0).strip()
                if value.find(res) == 0:
                    vil = re.sub(u'\s+с\/с', u'', res)
                    vil = vil.strip()
                    address_sub = re.sub(res, '', value)
                    region = self.get_region(vil) or u""
                    city_res = region + res + address_sub
            elif np:
                res = np.group(0).strip()
                if value.find(res) == 0:
                    vil = re.sub(u'н\.п\.\s*', u'', res)
                    vil = vil.strip()
                    address_sub = re.sub(res, '', value)
                    region = self.get_region(vil) or u""
                    city_res = region + res + address_sub
            elif p_only:
                res = p_only.group(0).strip()
                if value.find(res) == 0:
                    vil = re.sub(u'п\.\s*', u'', res)
                    vil = vil.strip()
                    address_sub = re.sub(res, '', value)
                    region = self.get_region(vil) or u""
                    city_res = region + res + address_sub

            if city_res:
                city = city_res
            else:
                city = value

        return city

    def get_region(self, city):
        for k, v in BY_CITIES.iteritems():
            if city in v:
                return k + u","
        return False

    def get_region_district(self, city):
        for k, v in BY_DISTRICT.iteritems():
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
        phone = re.sub(u'\(', u',(', phone)
        if ';' in phone:
            phns = phone.split(';')
        else:
            phns = phone.split(',')

        phone_code = ''
        phone_type = u'phone'
        for ph in phns:
            if ph.strip():
                if u"факс" in ph:
                    phone_type = u"fax"
                ph = ph.strip()
                ph = re.sub('^\+375','',ph)
                ph = re.sub('\D', '', ph)
                ph = re.sub('^8','',ph)
                ph = re.sub('^0','',ph)
                if len(ph)>9:
                    ph = re.sub('^0','',ph)

                if len(ph)<7:
                    ph = phone_code + ph
                    ph = re.sub('\D','',ph)

                for code in BY_TYL_CODES:
                    if ph.find(code) == 0:
                        phones.append([u"+375" + u" (" + code + u") " + re.sub("^%s" % code, '', ph), phone_type])
                        phone_code = code
                        break

        return phones

    def get_tags(self, s, open_delim  ='<', close_delim ='>'):
        while True:
            start = s.find(open_delim)
            end = s.find(close_delim)

            if -1 < start < end:
                start += len(open_delim)
                yield s[start:end].strip()
                s = s[end+len(close_delim):]
            else:
                return

    def process_item(self, item, spider):
        address = item['address']
        phones = item['phone']
        fuels = item['fuels']
        services = item['services']
        payments = item['payments']
        latitude = item['latitude']
        longitude = item['longitude']

        if not phones:
            phones = u"(232) 793333"

        self.count_item += 1
        xml_item = etree.SubElement(self.xml, 'company')
        xml_id = etree.SubElement(xml_item, 'company-id')
        company_id_address = address + unicode(latitude) + unicode(longitude)
        xml_id.text = self.company_id(company_id_address)
        # xml_address_raw = etree.SubElement(xml_item, 'address_raw', lang=u'ua')

        xml_name = etree.SubElement(xml_item, 'name', lang=u'ru')
        xml_name.text = u"Белоруснефть"

        xml_address = etree.SubElement(xml_item, 'address', lang=u'ru')
        # address = self.get_city(address)

        address = re.sub(u'\d{6}', '', address).strip(';, .')
        address = address.replace('..', '.')
        address = address.replace(u'а.г.', u'аг.')
        address = address.replace(u'Республика Беларусь', '').strip(';, .')

        address = self.get_city(address)
        address = self.get_result_city(address)
        address = self.get_result_cc(address)
        xml_address.text = address
        #
        # xml_phones_raw = etree.SubElement(xml_item, 'phones_raw')
        # xml_phones_raw.text = ''.join(item['phone'])

        xml_country = etree.SubElement(xml_item, 'country', lang=u'ru')
        xml_country.text = u"Беларусь"

        xml_coordinates = etree.SubElement(xml_item, 'coordinates')

        xml_lon = etree.SubElement(xml_coordinates, 'lon')
        xml_lon.text = longitude

        xml_lat = etree.SubElement(xml_coordinates, 'lat')
        xml_lat.text = latitude

        for phone in self.validate_phones(phones):
            xml_phone = etree.SubElement(xml_item, 'phone')
            xml_phone_number = etree.SubElement(xml_phone, 'number')
            xml_phone_number.text = phone[0]
            xml_phone_type = etree.SubElement(xml_phone, 'type')
            xml_phone_type.text = phone[1]
            xml_phone_ext = etree.SubElement(xml_phone, 'ext')
            xml_phone_info = etree.SubElement(xml_phone, 'info')

        xml_url = etree.SubElement(xml_item, 'url')
        xml_url.text = u"http://www.belorusneft.by"

        xml_rubric = etree.SubElement(xml_item, 'rubric-id')
        xml_rubric.text = u"184105274"

        if re.search(u"title='Газ'", fuels):
            xml_rubric2 = etree.SubElement(xml_item, 'rubric-id')
            xml_rubric2.text = u"184105272"

        xml_date = etree.SubElement(xml_item, 'actualization-date')
        xml_date.text = unicode(int(round(time.time() * 1000)))

        for tag in self.get_tags(fuels):
            for k in FUELS:
                if FUELS[k] in tag:
                    xml_feature_multiple = etree.SubElement(xml_item, 'feature-enum-multiple', name="fuel", value=k)

        for tag in self.get_tags(services):
            for k in ADDITIONAL:
                if ADDITIONAL[k] in tag:
                    xml_feature_service_car = etree.SubElement(xml_item, 'feature-enum-multiple', name="additional_services_cars", value=k)

        for tag in self.get_tags(payments):
            for k in FUEL_CARDS:
                if FUEL_CARDS[k] in tag:
                    xml_feature_cards = etree.SubElement(xml_item, 'feature-enum-multiple', name="fuel_cards", value=k)


        for tag in self.get_tags(payments):
            for k in CREDIT_CARD:
                if CREDIT_CARD[k] in tag:
                    xml_feature_credit_card = etree.SubElement(xml_item, 'feature-boolean', name=k, value="1")

        for tag in self.get_tags(services):
            for k in SERVICES:
                if SERVICES[k] in tag:
                    xml_feature = etree.SubElement(xml_item, 'feature-boolean', name=k, value="1")



        company_valid = etree.tostring(xml_item, pretty_print=True, encoding='unicode')
        company_valid = StringIO.StringIO(company_valid)
        valid = etree.parse(company_valid)
        if not relaxng.validate(valid):
            raise DropItem

    def close_spider(self, spider):
        doc = etree.tostring(self.xml, pretty_print=True, encoding='unicode')
        sout.write('<?xml version="1.0" encoding="UTF-8" ?>' + '\n')
        sout.write(doc)
