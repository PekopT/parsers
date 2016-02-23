#!/usr/bin/env python
# -*- coding: utf-8 -*-

import scrapy

from pharmacykiev.items import PharmacykievItem



class PharmacykievSpider(scrapy.Spider):
    name = "pharmacykiev"
    allowed_domains = ["pharmacy.kiev.ua"]
    start_urls = [
        "http://pharmacy.kiev.ua/p/aptechna-merezha/",
    ]

    def parse(self, response):
        for href in response.xpath('//table[@id="post-table"]/tr/td[1]/a/@href'):
            if href:
                url = response.urljoin(href.extract())
                yield scrapy.Request(url, callback=self.parse_page)

    def parse_page(self, response):
        item = PharmacykievItem()
        item['name'] = response.css('h2 span::text').extract()[0]
        item['url'] = response.url
        item['address'] = response.xpath("//div[@class='page-content']/p[1]/text()").extract()[0]
        phone_patterns = "//div[@class='page-content']/p[re:test(text(),'%s')]/text()" % u'[Т|т]ел\.'
        item['phone'] = response.xpath(phone_patterns).extract()
        yield item