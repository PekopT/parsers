# -*- coding: utf-8 -*-
import re
import scrapy

from scrapy.utils.log import configure_logging
from tehnoskarb.items import TehnoskarbItem

class TehnoskarbSpider(scrapy.Spider):
    name = "tehnoskarb"
    allowed_domains = ["tehnoskarb.com.ua", "ua.tehnoskarb.com.ua"]
    start_urls = [
        "http://tehnoskarb.com.ua/shops_list/",
    ]

    def parse(self, response):
        for item in response.xpath("//table[@id='shops_list']/tr[@class='district']/td[2]/a/@href"):
            href = item.extract()
            if href:
                url = response.urljoin(href)
                yield scrapy.Request(url, callback=self.parse_page_rus)

    def parse_page_rus(self, response):
        item = TehnoskarbItem()
        item['address_rus'] = response.xpath("//div[@class='container column1 shop_page']/h1/text()").extract()
        item['working_time_ru'] = response.xpath("//div[@class='shop_info']/div/div[@class='tel']/div/text()").extract()
        item['add_url_ru'] = response.url
        url = re.sub('tehnoskarb\.com', 'ua.tehnoskarb.com', response.url)
        request = scrapy.Request(url, callback=self.parse_page_ua)
        request.meta['item'] = item
        yield request

    def parse_page_ua(self, response):
        item = response.meta['item']
        item['name'] = u"Ua test"
        item['address_ua'] = response.xpath("//div[@class='container column1 shop_page']/h1/text()").extract()
        item['working_time_ua'] = response.xpath("//div[@class='shop_info']/div/div[@class='tel']/div/text()").extract()
        item['phone'] = response.xpath("//div[@class='shop_info']/div/div[@class='tel']/text()").extract()
        item['add_url_ua'] = response.url
        yield item