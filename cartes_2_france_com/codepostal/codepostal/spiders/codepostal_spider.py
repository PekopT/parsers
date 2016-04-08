# -*- coding: utf-8 -*-

import scrapy

from codepostal.items import CodepostalItem

class CodepostalSpider(scrapy.Spider):
    name = "codepostal"
    allowed_domains = ["www.codes-villes.com"]

    start_urls = (
        'http://www.codes-villes.com/codepostal/75056-paris.php?insee=75056&ville=paris',
    )

    def parse(self, response):
        codepostals_parent = response.xpath("//div[@id='contenu3']/div/h1[re:test(text(),'^Les')]/parent::div/parent::div")
        codepostals = codepostals_parent.xpath("table[@id='postal']/tr")
        for cp in codepostals:
            name_info = cp.xpath("td[1]/a/text()")
            if name_info:
                name = name_info.extract()[0]
                address = cp.xpath("td[3]/text()").extract()
                postal = cp.xpath("td[4]/text()").extract()
                # full_address = address + ',' +  postal
                item = CodepostalItem()
                item['name'] = name
                item['category'] = u"ECOLE DE NIVEAU ELEMENTAIRE"
                item['address'] = address
                item['postal'] = postal
                yield item
