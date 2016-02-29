# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from sys import stdout
import time
import StringIO
import re

from codecs import getwriter
from lxml import etree
from scrapy.exceptions import DropItem
from phonecodes import BY_TYL_CODES,CODE_OPERATORS,CITIES
from schema_org import SCHEMA_ORG

sout = getwriter("utf8")(stdout)
relaxng_doc = etree.parse(SCHEMA_ORG)
relaxng = etree.RelaxNG(relaxng_doc)


class FsvpsPipeline(object):

    def __init__(self):
        self.count_item = 0
        self.valid_count = 0
        self.ns = {"xi": 'http://www.w3.org/2001/XInclude'}
        self.xml = etree.Element('companies', version='2.1', nsmap=self.ns)
        self.save_data = dict()
        self.save_phones = dict()

    def company_id(self):
        return u'0005' + unicode(self.count_item)

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

            for phone in phns:
                if phone.strip():
                    phone = re.sub('8-10-380-.{3}|8-10-383-.{3}','3652',phone)
                    phone = re.sub("^8", '', phone)
                    phone = re.sub(u'\(доб.*\d+\)','',phone)
                    phone = re.sub('\D','',phone)
                    status = False

                    if len(phone)>3:
                        if len(phone)>10:
                            phone = phone[-10:]

                        for code in BY_TYL_CODES:
                            if phone.find(code) == 0:
                                phones.append(u"+7" + u" (" + code + u") " + re.sub("^%s" % code, '', phone))
                                status = True
                                break

                        if not status:
                            for code in CODE_OPERATORS:
                                if phone.find(code) == 0:
                                    phone = u"+7" + u" (" + code + u") " + re.sub("^%s" % code, '', phone)
                            if len(phone)<8 and phones:
                                code_search = re.search(u'^.+\)',phones[0]).group(0)
                                phone = code_search + phone

                            phones.append(phone)
        return phones

    def validate_address(self, value):
        try_split = re.split(u'\d+,?', value)
        if len(try_split) > 1:
            addr = try_split[1]
        else:
            addr = try_split[0]
        return addr

    def validate_test_address(self,value):
        pass

    def remove_postal(self,value):
       value = re.sub(r"\d{6}",'',value)
       value = re.sub(u"«|»|\(|\)",'',value)
       value = re.sub(u'&#13;|&lt;|&gt;|<|>|\/li|\r','',value)
       value.rstrip(',) ')
       return value

    def validate_otdel_name(self,name,type):
        if type == 1:
            return True
        keywords = [u"Межрайонный",u"надзор",u"контрол",u"межрай"]
        pattern = u'|'.join(keywords)
        if re.search(pattern,name,re.IGNORECASE):
            return True
        else:
            return False

    def split_organization(self,value):
        new_value = re.sub(u"\s+", '', value)
        new_value = re.sub(u"г\.,", '', value)
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
            if re.search(u'^тел|Тел', item, re.IGNORECASE):
                phone = item.strip()
                phns = re.split('; |,', phone)
                for ph in phns:
                    ph = re.sub(u'тел|Тел','',ph).lstrip(',:.')
                    phones.append(ph)

        return phones

    def get_phone_raw(self,value):
        out = u''
        items = value.split('<br>')
        for item in items:
            if re.search(u'^тел|Тел', item, re.IGNORECASE):
                phone = item.strip()
                phone = re.sub(u'&#13;|&lt;|&gt;|<|>|\/li|\r','',phone)
                out +=  phone + u"||"

        return out

    def get_faxes_from_content(self,value):
        phones = []
        items = value.split('<br>')
        for item in items:
            if re.search(u'^факс|Факс', item, re.IGNORECASE):
                phone = item.strip()
                phns = re.split('; |,', phone)
                for ph in phns:
                    ph = re.sub(u'факс|Факс','',ph).lstrip(',:.')
                    phones.append(ph)

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

    def address_formatter(self,value,url):
        value = value.rstrip(',.; ').lstrip(',( ')
        if re.search(u'^г\.[А-Яа-я]+$',value):
            value = self.get_parent_address(url)
        if re.search(u"^[ул\.|с\.|п\.]",value):
            value = self.get_parent_address(url)

        test_val = re.sub('\D','',value)
        if len(test_val) > 9:
            value = self.get_parent_address(url)

        value = re.sub(u'.+г\.',u'г.',value)
        return value

    def get_parent_address(self,check_url):
        address = self.save_data[check_url].rstrip(',.; ').lstrip(',( ')
        return address


    def get_city(self,value):
        pattern = u'г\.\s*[А-Яа-я\-]+'
        cities = {
            u"Нижний":u"Нижегородская область город Нижний Новгород",
            u"Великий": u"Новгородская область город Великий Новгород",
        }
        m=re.search(pattern,value)
        if m:
            res = m.group(0).strip()
            city = re.sub(u'г\.\s*','',res)
            region = self.get_region(city)
            if region:
                city = region + u' город ' + city + re.sub(pattern,'',value)
            elif cities[city]:
                end_address = re.sub(pattern,'',value)
                end_address = re.sub(u'Новгород','',end_address)
                city = cities[city] + end_address
            else:
                city = value
        else:
            city = value

        return city

    def get_region(self,city):
        for k, v in CITIES.iteritems():
            if city in v:
                return k

        return False

    def process_item(self, item, spider):
        name = self.validate_str(item['name'])
        name = re.sub('\(.*\)','',name)
        type = item['type']

        if not self.validate_otdel_name(name, type):
           raise DropItem
        
        url = item['url']

        if type == 1:
            address = self.validate_str(item['address'])
            address = self.remove_postal(address)
            email = self.validate_str(item['email'])
            phones = item['phone']
            phone_raw = '||'.join(item['address'])
            faxes = item['fax']
            self.save_data[url] = address
            self.save_phones[url] = phones
            url_to_xml = url
        else:
            content = item["content"]
            address = self.remove_postal(self.get_address_from_content(content))
            phone_raw = self.get_phone_raw(content)
            phones = self.get_phone_from_content(content)
            faxes = self.get_faxes_from_content(content)
            email = ""
            url_add = url
            url_to_xml = 'http://www.fsvps.ru'

        organizations = self.split_organization(address)
        address = organizations[0].rstrip(',.; ').lstrip(',( ')
        check_url = url[:-15]
        if not address:
            address = self.get_parent_address(check_url)

        address = re.sub(u'&#13;|&lt;|&gt;|<|>|\/li|\r','',address).strip().rstrip(',;)').lstrip(',(')

        self.count_item +=1
        xml_item = etree.SubElement(self.xml, 'company')
        xml_id = etree.SubElement(xml_item, 'company-id')
        xml_id.text = self.company_id()

        xml_name = etree.SubElement(xml_item, 'name', lang=u'ru')
        name = re.sub(u'&#13;|\r','',name).strip()

        m = re.search(u'оссельхоз',name)
        if not m:
            name = u'Россельхознадзор ' + name

        xml_name.text = name

        address = self.address_formatter(address,check_url)

        address = self.get_city(address)

        xml_address = etree.SubElement(xml_item, 'address', lang=u'ru')
        xml_address.text = address

        if len(phones) == 0:
            url_check = url[:-15]
            phones = self.save_phones[url_check]

        for phone in self.validate_phones(phones):
            xml_phone = etree.SubElement(xml_item, 'phone')
            xml_phone_number = etree.SubElement(xml_phone, 'number')
            xml_phone_number.text = phone.strip()
            xml_phone_type = etree.SubElement(xml_phone, 'type')
            xml_phone_type.text = u'phone'
            xml_phone_ext = etree.SubElement(xml_phone, 'ext')
            xml_phone_info = etree.SubElement(xml_phone, 'info')

        for fax in self.validate_phones(faxes):
            # if phone.strip():
            xml_fax = etree.SubElement(xml_item, 'phone')
            xml_fax_number = etree.SubElement(xml_fax, 'number')
            xml_fax_number.text = fax.strip()
            xml_fax_type = etree.SubElement(xml_fax, 'type')
            xml_fax_type.text = u'fax'
            xml_phone_ext = etree.SubElement(xml_fax, 'ext')
            xml_phone_info = etree.SubElement(xml_fax, 'info')

        if email:
            xml_email = etree.SubElement(xml_item, 'email')
            xml_email.text = email

        xml_url = etree.SubElement(xml_item, 'url')
        xml_url.text = url_to_xml

        if type == 2:
            xml_add_url = etree.SubElement(xml_item,'add-url')
            xml_add_url.text = url_add

        xml_rubric = etree.SubElement(xml_item, 'rubric-id')
        xml_rubric.text = u"184105646"

        xml_date = etree.SubElement(xml_item, 'actualization-date')
        xml_date.text = unicode(int(round(time.time() * 1000)))

        company_valid = etree.tostring(xml_item, pretty_print=True, encoding='unicode')
        # out = re.sub('\sxmlns:xi="http://www.w3.org/2001/XInclude"','',out)
        company_valid = StringIO.StringIO(company_valid)

        valid = etree.parse(company_valid)
        if not relaxng.validate(valid):
            raise DropItem

        if (len(organizations) > 1):
            self.valid_count +=1
            xml_item2 = etree.SubElement(self.xml, 'company')
            xml_id2 = etree.SubElement(xml_item2, 'company-id')
            xml_id2.text = self.company_id() + u'_2'

            xml_name2 = etree.SubElement(xml_item2, 'name', lang=u'ru')
            xml_name2.text = name

            xml_address2 = etree.SubElement(xml_item2, 'address', lang=u'ru')
            xml_address2.text = organizations[1].rstrip(',.; ').lstrip(',( ')

            for phone in self.validate_phones(phones):
                xml_phone2 = etree.SubElement(xml_item2, 'phone')
                xml_phone_number2 = etree.SubElement(xml_phone2, 'number')
                xml_phone_number2.text = phone.strip()
                xml_phone_type2 = etree.SubElement(xml_phone2, 'type')
                xml_phone_type2.text = u'phone'
                xml_phone_ext2 = etree.SubElement(xml_phone2, 'ext')
                xml_phone_info2 = etree.SubElement(xml_phone2, 'info')

            xml_url2 = etree.SubElement(xml_item2, 'url')
            xml_url2.text = url

            if type == 2:
                xml_add_url = etree.SubElement(xml_item2,'add-url')
                xml_add_url.text = url_add

            xml_rubric2 = etree.SubElement(xml_item2, 'rubric-id')
            xml_rubric2.text = u"184105646"

            xml_date2 = etree.SubElement(xml_item2, 'actualization-date')
            xml_date2.text = unicode(int(round(time.time() * 1000)))

    def close_spider(self, spider):
        doc = etree.tostring(self.xml, pretty_print=True, encoding='unicode')
        sout.write('<?xml version="1.0" encoding="UTF-8" ?>' + '\n')
        sout.write(doc)
