# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from sys import stdout

import re
from codecs import getwriter

sout = getwriter("utf8")(stdout)

TURK_CITIES = {
    u"Adana": u"322",
    u"Adıyaman": u"416",
    u"Afyonkarahisar": u"272",
    u"Ağrı": u"472",
    u"Amasya": u"358",
    u"Ankara": u"312",
    u"Antalya": u"242",
    u"Artvin": u"466",
    u"Aydın": u"256",
    u"Balıkesir": u"266",
    u"Bilecik": u"228",
    u"Bingöl": u"426",
    u"Bitlis": u"434",
    u"Bolu": u"374",
    u"Burdur": u"248",
    u"Bursa": u"224",
    u"Çanakkale": u"286",
    u"Çankırı": u"376",
    u"Çorum": u"364",
    u"Denizli": u"258",
    u"Diyarbakır": u"412",
    u"Edirne": u"284",
    u"Elazığ": u"424",
    u"Erzincan": u"446",
    u"Erzurum": u"442",
    u"Eskişehir": u"222",
    u"Gaziantep": u"342",
    u"Giresun": u"454",
    u"Gümüşhane": u"456",
    u"Hakkâri": u"438",
    u"Hatay": u"326",
    u"Isparta": u"246",
    u"Mersin": u"324",
    u"İstanbul": u"212,216",
    u"İzmir": u"232",
    u"Kars": u"474",
    u"Kastamonu": u"366",
    u"Kayseri": u"352",
    u"Kırklareli": u"288",
    u"Kırşehir": u"386",
    u"Kocaeli": u"262",
    u"Konya": u"332",
    u"Kütahya": u"274",
    u"Malatya": u"422",
    u"Manisa": u"236",
    u"Kahramanmaraş": u"344",
    u"Mardin": u"482",
    u"Muğla": u"252",
    u"Muş": u"436",
    u"Nevşehir": u"384",
    u"Niğde": u"388",
    u"Ordu": u"452",
    u"Rize": u"464",
    u"Sakarya": u"264",
    u"Samsun": u"362",
    u"Siirt": u"484",
    u"Sinop": u"368",
    u"Sivas": u"346",
    u"Tekirdağ": u"282",
    u"Tokat": u"356",
    u"Trabzon": u"462",
    u"Tunceli": u"428",
    u"Şanlıurfa": u"414",
    u"Uşak": u"276",
    u"Van": u"432",
    u"Yozgat": u"354",
    u"Zonguldak": u"372",
    u"Aksaray": u"382",
    u"Bayburt": u"458",
    u"Karaman": u"338",
    u"Kırıkkale": u"318",
    u"Batman": u"488",
    u"Şırnak": u"486",
    u"Bartın": u"378",
    u"Ardahan": u"478",
    u"Iğdır": u"476",
    u"Yalova": u"226",
    u"Karabük": u"370",
    u"Kilis": u"348",
    u"Osmaniye": u"328",
    u"Düzce": u"380",
}


class BpetgenelPipeline(object):
    header = u"original-id,name-tr,name-alt-tr,address-tr,country-tr,province-tr," \
             u"district-tr,sub-district-tr,locality-tr,street-tr,street-side-tr,house," \
             u"address-add-tr,landmark-tr,lon,lat,phone,url,rubric-id,working-time," \
             u"actualization-date,rubric-keys,source-url,rubric-tr,chain-id"

    def __init__(self):
        sout.write(self.header + "\n")

    def validate_int(self, value, length, suffix=False):
        if type(value) == list:
            val = value[0] if value else None
            if val is None:
                return False
        else:
            val = value

        if length is not False:
            val = re.sub("\D", "", val)
            if len(val) != length:
                return False
        return int(val.strip())

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

    def validate_tel(self, value):
        if type(value) == list:
            for v in value:
                if v.strip() and v.strip() != 'T:':
                    val = v.strip()
                    break
                else:
                    val = None
            if val is None:
                return False
        else:
            val = value.strip()

        return u'+90 (' + val[0:3].strip() + u') ' + val[3:].strip()

    def process_item(self, item, spider):
        name = item['name']
        address = item['address'].strip()
        phone = self.validate_tel(item['phone'])
        fax = item['fax']
        url = item['url']
        latitude =  item['latitude'].strip()
        longitude = item['longitude'].strip()
        city = item['city'].strip()
        pattern = u'\<[^>]*\>'
        name = re.sub(pattern, '', name).strip()
        address = re.sub(u',','',address)
        sout.write(','.join([
            '',  # original-id
            name,
            '',  # name-alt-tr
            address,
            u'Türkiye',  # country-tr
            city[4:],
            '',  # district-tr
            '',  # sub-district-tr
            '',  # locality-tr,
            '',  # street-tr,
            '',  # street-side-tr,
            '',  # house,
            '',  # address-add-tr,
            '',  # landmark-tr,
            longitude,
            latitude,
            phone,
            url,  # url,
            '',  # rubric-id,
            '',  # working-time,
            '',  # actualization-date,
            '',  # rubric-keys,
            '',  # source-url,
            '',  # rubric-tr,
            '',  # chain-id
        ]) + "\n")
