#!/usr/bin/env python
# -*- coding: utf-8 -*-

import scrapy

from ukrtelecom.items import UkrtelecomItem



class UkrtelecomSpider(scrapy.Spider):
    name = "ukrtelecom"
    allowed_domains = ["www.ukrtelecom.ua"]
    start_urls = [
        "http://www.ukrtelecom.ua/services/customers/where_to_buy",
    ]

    def parse(self, response):
        for href in response.xpath('//table[@class="invizible"]/tr/td/a/@href'):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_page)

    def parse_page(self, response):
        items = response.xpath("//table[@id='telecomservice']//tr[not(@class)]")
        if items:
            del items[0]

        for item in items:
            ukrtelecom = UkrtelecomItem()
            ukrtelecom['name'] = u"Укртелеком"
            ukrtelecom['url'] = response.url
            ukrtelecom['phone'] = u"0 (800) 50-68-00"
            ukrtelecom['address'] = item.xpath('td[2]//p/text()').extract()
            ukrtelecom['city'] = item.xpath('td[1]/p/text()').extract()
            ukrtelecom['working_time'] = item.xpath('td[3]//p/text()').extract()
            yield ukrtelecom

