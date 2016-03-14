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

sout = getwriter("utf8")(stdout)

relaxng_doc = etree.parse(SCHEMA_ORG)
relaxng = etree.RelaxNG(relaxng_doc)


class PharmacykievPipeline(object):
    def __init__(self):
        self.count_item = 0
        self.ns = {"xi": 'http://www.w3.org/2001/XInclude'}
        self.xml = etree.Element('companies', version='2.1', nsmap=self.ns)

    def company_id(self):
        return u'0099' + unicode(self.count_item)

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

    def is_pharma_production(self, value):
        value = value.strip()
        m = re.search(u'Виробничі', value)
        if m:
            return True
        return False

    def is_pharma_homeopathic(self, value):
        value = value.strip()
        m = re.search(u'Гомеопатичні', value)
        if m:
            return True
        return False

    def is_payment_by_credit_card(self, value):
        value = value.strip()
        m = re.search(u'Працюють цілодобово', value)
        if m:
            return True
        return False

    def format_work_time(self,work_time_list):
        work_time = ''
        for work in work_time_list:
            if work.lower().find(u"вихідний") == -1:
                work_time += re.sub('\s', '', work) + ' , '

        return work_time[:-3]


    def process_item(self, item, spider):
        name = u"Аптека Фармация"
        name_ukr = u"Аптека Фармація"
        name_other = item['name']
        url = item['url']
        address = item['address'].strip(',;. ')
        phones = item['phone']
        indication = item['indication']
        working_time = ''.join(item['pn_pt'])
        sat_time = ''.join(item['sat'])
        sunday_time = ''.join(item['sunday'])

        work_time_list = [working_time,sat_time,sunday_time]
        work_time = self.format_work_time(work_time_list)

        self.count_item += 1
        xml_item = etree.SubElement(self.xml, 'company')
        xml_id = etree.SubElement(xml_item, 'company-id')
        xml_id.text = self.company_id()

        xml_name = etree.SubElement(xml_item, 'name', lang=u'ru')
        xml_name.text = name

        xml_name_ukr = etree.SubElement(xml_item, 'name', lang=u'ua')
        xml_name_ukr.text = name_ukr

        xml_name_other = etree.SubElement(xml_item, 'name-other', lang=u'ru')
        xml_name_other.text = name_other

        xml_address = etree.SubElement(xml_item, 'address', lang=u'ua')
        xml_address.text = address

        xml_country = etree.SubElement(xml_item, 'country', lang=u'ua')
        xml_country.text = u"Україна"

        xml_phone_main = etree.SubElement(xml_item, 'phone')
        xml_phone_number_main = etree.SubElement(xml_phone_main, 'number')
        xml_phone_number_main.text = u"+380 (44) 407-90-90"
        xml_phone_type_main = etree.SubElement(xml_phone_main, 'type')
        xml_phone_type_main.text = u'phone'
        xml_phone_main_ext = etree.SubElement(xml_phone_main, 'ext')
        xml_phone_main_info = etree.SubElement(xml_phone_main, 'info')

        for phone in self.validate_phones(phones):
            xml_phone = etree.SubElement(xml_item, 'phone')
            xml_phone_number = etree.SubElement(xml_phone, 'number')
            xml_phone_number.text = phone.strip()
            xml_phone_type = etree.SubElement(xml_phone, 'type')
            xml_phone_type.text = u'phone'
            xml_phone_ext = etree.SubElement(xml_phone, 'ext')
            xml_phone_info = etree.SubElement(xml_phone, 'info')

        xml_url = etree.SubElement(xml_item, 'url')
        xml_url.text = u"http://pharmacy.kiev.ua"

        xml_url_add = etree.SubElement(xml_item, 'add-url')
        xml_url_add.text = url
        sat_time = re.sub(u'Субота', u'Субота.', sat_time)
        sunday_time = re.sub(u'Неділя', u'Неділя.', sunday_time)
        work_time_list = [working_time, sat_time, sunday_time]
        xml_working_time = etree.SubElement(xml_item, 'working-time',lang=u"ua")

        xml_working_time.text = self.format_work_time(work_time_list)

        xml_rubric = etree.SubElement(xml_item, 'rubric-id')
        xml_rubric.text = u"184105932"

        xml_date = etree.SubElement(xml_item, 'actualization-date')
        xml_date.text = unicode(int(round(time.time() * 1000)))

        if self.is_pharma_production(indication):
            xml_prod_pharma = etree.SubElement(xml_item, 'feature-boolean', name="production_pharmacy", value="1")

        if self.is_pharma_homeopathic(indication):
            xml_homeopathic_pharma = etree.SubElement(xml_item, 'feature-boolean', name="homeopathic_pharmacy", value="1")

        if self.is_payment_by_credit_card(indication):
            xml_payment_by_credit_card = etree.SubElement(xml_item, 'feature-boolean', name="payment_by_credit_card", value="1")

        company_valid = etree.tostring(xml_item, pretty_print=True, encoding='unicode')
        company_valid = StringIO.StringIO(company_valid)
        valid = etree.parse(company_valid)
        # if not relaxng.validate(valid):
        #     raise DropItem

    def close_spider(self, spider):
        doc = etree.tostring(self.xml, pretty_print=True, encoding='unicode')
        sout.write('<?xml version="1.0" encoding="UTF-8" ?>' + '\n')
        sout.write(doc)
