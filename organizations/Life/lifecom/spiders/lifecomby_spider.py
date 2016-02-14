# -*- coding: utf-8 -*-
from lifecom.items import LifecomItem
import scrapy


class LifecombySpider(scrapy.Spider):
    name = "lifecomby"
    allowed_domains = ["www.life.com.by"]
    start_urls = (
        'http://www.life.com.by/private/salons/',
    )

    def parse(self, response):
        for href in response.xpath('//div[@id="city-list"]/a/@href'):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_office_page)

    def parse_office_page(self, response):
        city_name = response.xpath('//div[@class="city_name"]/text()').extract()
        for item in response.xpath('//div[@class="salon"]'):
            office = LifecomItem()
            office['name'] = item.xpath('div/div[@class="name"]/a/text()').extract()
            office['address'] = item.xpath('div/div[@class="adress"]/text()').extract()
            office['phone'] = item.xpath('div/div[@class="phone"]/text()').extract()
            office['url'] = response.url
            office['city'] = city_name
            days = [x.strip() for x in item.xpath('div[@class="cont"]//tr[1]/td/text()').extract()]
            times = [x.strip() for x in item.xpath('div[@class="cont"]//tr[2]/td/text()').extract()]
            office['time'] = dict(zip(days, times))
            yield office
