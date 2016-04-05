#!/usr/bin/env python
# -*- coding: utf-8 -*-

import scrapy
import re

from fsvps.items import FsvpsItem


class FsvpsSpider(scrapy.Spider):
    name = "fsvps"
    allowed_domains = ["www.fsvps.ru"]
    start_urls = [
        "http://www.fsvps.ru/fsvps/structure/terorgs",
    ]

    def parse(self, response):
        for href in response.xpath('//table[@class="item"]//a[starts-with(@href,"/fsvps/structure/terorgs")]/@href'):
            url = response.urljoin(href.extract())
            if not url.encode('utf-8').endswith('.html'):
                yield scrapy.Request(url, callback=self.parse_page)

    def parse_page(self, response):
        sel = response.xpath("//div[@class='nText']")
       # new_adress_pattern = "//p[re:test(@class,'noin?dent|generic') and re:test(text(),'%s')]/text()" % u'Адр|адр'
        address_pattern = "//p[re:test(@class,'noin?dent')][span[re:test(text(),'%s')]]/span[@class='big']/text()" \
                          % u'Адр|адр|есторасполож'

        phone_pattern = "//p[re:test(@class,'noin?dent')][span[re:test(text(),'%s')]]/span[@class='big']/text()" \
                        % u'^[Т|т]ел'
        site_pattern = "//p[re:test(@class,'noin?dent')][span[re:test(text(),'%s')]]/span[@class='big']/a/text()" \
                        % u'^[С|с]айт'

        fax_pattern = "//p[re:test(@class,'noin?dent')][span[re:test(text(),'%s')]]/span[@class='big']/text()" \
                        % u'^Факс|факс'

        email_pattern = "//p[re:test(@class,'noin?dent')][span[re:test(text(),'%s')]]/a/text()" % 'mail'

        out_item = FsvpsItem()
        out_item['name'] = response.xpath("//td[@id='contenttd']/div/h2/text()").extract()



        out_item['phone'] = sel.xpath(phone_pattern).extract()
        if len(out_item['phone']) == 0:
            phone_pattern2 = "//p[re:test(@class,'generic')][span[re:test(text(),'%s')]]/text()" % u'^Тел|тел'
            out_item['phone'] = sel.xpath(phone_pattern2).extract()
            if len(out_item['phone']) == 0:
                phone_pattern3 = "//p[re:test(@class,'noin?dent')][b[re:test(text(),'%s')]]/span[@class='big']/text()" \
                          % u'^Тел|тел'
                out_item['phone'] = sel.xpath(phone_pattern3).extract()
                if len(out_item['phone']) == 0:
                    phone_pattern4 = "//p[re:test(@class,'noin?dent')][span[re:test(text(),'%s')]]/text()" % u'^Тел|тел'
                    out_item['phone'] = sel.xpath(phone_pattern4).extract()

        out_item['site_url'] = sel.xpath(site_pattern).extract()
        if len(out_item['site_url']) == 0:
            site_pattern2 = "//p[re:test(@class,'generic')][span[re:test(text(),'%s')]]/a/text()" % u'^Сайт|сайт'
            out_item['site_url'] = sel.xpath(site_pattern2).extract()
            if len(out_item['site_url']) == 0:
                site_pattern3 = "//p[re:test(@class,'noin?dent')][b[re:test(text(),'%s')]]/a/text()" \
                          % u'^Сайт|сайт'
                out_item['site_url'] = sel.xpath(site_pattern3).extract()
                if len(out_item['site_url']) == 0:
                    site_pattern4 = "//p[re:test(@class,'noin?dent')][span[re:test(text(),'%s')]]/a/text()" % u'^Сайт|сайт'
                    out_item['site_url'] = sel.xpath(site_pattern4).extract()


        out_item['address'] = sel.xpath(address_pattern).extract()
        if len(out_item['address']) == 0:
            address_pattern_double = "//p[re:test(@class,'generic')][span[contains(text(),'%s')]]/text()" % u'Адр'
            out_item['address'] = sel.xpath(address_pattern_double).extract()
            if len(out_item['address']) == 0:
                address_pattern3 = "//p[re:test(@class,'noin?dent')][b[re:test(text(),'%s')]]/span[@class='big']/text()" \
                          % u'Адр|адр'
                out_item['address'] = sel.xpath(address_pattern3).extract()

        out_item['fax'] = sel.xpath(fax_pattern).extract()

        if len(out_item['fax']) == 0:
             fax_pattern2 = "//p[re:test(@class,'generic')][span[re:test(text(),'%s')]]/text()" % u'Факс|факс'
             out_item['fax'] = sel.xpath(fax_pattern2).extract()
             if len(out_item['fax']) == 0:
                 fax_pattern3 = "//p[re:test(@class,'noin?dent')][b[re:test(text(),'%s')]]/span[@class='big']/text()" \
                                % u'Факс|факс'
                 out_item['fax'] = sel.xpath(fax_pattern3).extract()
                 if len(out_item['fax']) == 0:
                    fax_pattern4 = "//p[re:test(@class,'noin?dent')][span[re:test(text(),'%s')]]/text()" % u'^Факс|факс'
                    out_item['fax'] = sel.xpath(fax_pattern4).extract()


        out_item['longitude'] = ''
        out_item['latitude'] = ''
        scripts = response.xpath("//div/script").extract()
        for sc in scripts:
            sc = sc.replace(" ",'').replace("\n","")
            m = re.search("YMaps\.GeoPoint\([0-9.,]+\)",sc)
            if m:
                res = m.group(0)
                res = res.replace("YMaps.GeoPoint(","").replace(")","")
                longitude, latitude  = res.split(',')
                out_item['longitude'] = longitude
                out_item['latitude'] = latitude


        out_item['email'] = sel.xpath(email_pattern).extract()
        out_item['type'] = 1
        out_item['url'] = response.url
        yield out_item

        links = response.xpath("//div[@class='linkholder']//a[re:test(@href,'structure.html$')]/@href")
        if len(links) > 0:
             for href in links:
                 url = response.urljoin(href.extract())
                 yield scrapy.Request(url, callback=self.parse_page_struct)

    def parse_page_struct(self, response):
        for item in response.xpath("//ol[@class='str']/li"):
            out_item = FsvpsItem()
            out_item['name'] = item.xpath('span/text()').extract()
            out_item['url'] = response.url
            out_item["content"] = item.extract()
            out_item['phone'] = []
            out_item['address'] = ""
            out_item['email'] = ""
            out_item['type'] = 2
            out_item['fax'] = ""
            yield out_item
