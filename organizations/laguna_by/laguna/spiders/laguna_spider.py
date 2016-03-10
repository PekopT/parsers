# -*- coding: utf-8 -*-
import scrapy

from laguna.items import LagunaItem
from laguna.pipelines import LagunaBelPipeline, LagunaKzPipeline

class LagunaBelSpider(scrapy.Spider):
    name = "lagunabel"
    allowed_domains = ["www.laguna.by"]
    start_urls = (
        'http://www.laguna.by/shops.html',
    )

    pipeline = set([
        LagunaBelPipeline,
    ])

    def parse(self, response):
        for href in response.xpath('//table[@class="shops_table"]/tbody/tr/td/ul/li/a/@href'):
            url = response.urljoin(href.extract())
            if u"84-belarus" in url:
                country = 'by'
                yield scrapy.Request(url, callback=self.parse_office_page, meta={'country':country})

    def parse_office_page(self, response):
        country = response.meta['country']
        items = response.xpath("//div[@id='content']/div[@class='item-page']/table[@class='shoplist_table']/tbody/tr")
        del items[0]
        for item in items:
            address = item.xpath("td[2]").extract()
            city = item.xpath("td[1]").extract()
            phone = item.xpath("td[4]").extract()
            working_time = item.xpath("td[3]").extract()
            land = u"Беларусь"
            oblast = response.xpath("//div[@id='content']/div[@class='item-page']/h2/text()").extract()[0]
            type=1
            office = LagunaItem()
            office['name'] = u''
            office['address'] = address
            office['phone'] = phone
            office['url'] = response.url
            office['city'] = city
            office['country'] = land
            office['oblast'] = oblast
            office['working_time'] = working_time
            office['type'] = type
            yield office


class LagunaKzSpider(scrapy.Spider):
    name = "lagunakz"
    allowed_domains = ["www.laguna.by"]
    start_urls = (
        'http://www.laguna.by/shops.html',
    )

    pipeline = set([
        LagunaKzPipeline,
    ])

    def parse(self, response):
        for href in response.xpath('//table[@class="shops_table"]/tbody/tr/td/ul/li/a/@href'):
            url = response.urljoin(href.extract())
            if u"87-kazakhstan" in url:
                country = 'kz'
                yield scrapy.Request(url, callback=self.parse_office_page, meta={'country':country})

    def parse_office_page(self, response):
        country = response.meta['country']
        items = response.xpath("//div[@id='content']/div[@class='item-page']/table[@class='shoplist_table']/tbody/tr")
        del items[0]
        for item in items:
            address = item.xpath("td[3]/text()").extract()
            city = item.xpath("td[1]/text()").extract()
            phone = item.xpath("td[4]/text()").extract()
            info = item.xpath("td[2]/text()").extract()
            working_time = u''
            land = u"Казахстан"
            oblast = u""
            type = 2

            office = LagunaItem()
            office['name'] = u''
            office['address'] = address
            office['phone'] = phone
            office['url'] = response.url
            office['city'] = city
            office['country'] = land
            office['oblast'] = oblast
            office['working_time'] = working_time
            office['type'] = type
            yield office


class LagunaSpider(scrapy.Spider):
    name = "laguna"
    allowed_domains = ["www.laguna.by"]
    start_urls = (
        'http://www.laguna.by/shops.html',
    )
    def parse(self, response):
        for href in response.xpath('//table[@class="shops_table"]/tbody/tr/td/ul/li/a/@href'):
            url = response.urljoin(href.extract())
            if u"87-kazakhstan" in url:
                country = 'kz'
            elif u"84-belarus" in url:
                country = 'by'
            else:
                country = 'ru'
            if 'ru' not in country:
                yield scrapy.Request(url, callback=self.parse_office_page, meta={'country':country})


    def parse_office_page(self, response):
        country = response.meta['country']

        items = response.xpath("//div[@id='content']/div[@class='item-page']/table[@class='shoplist_table']/tbody/tr")
        del items[0]
        for item in items:
            if 'by' in country:
                address = item.xpath("td[2]").extract()
                city = item.xpath("td[1]").extract()
                phone = item.xpath("td[4]").extract()
                working_time = item.xpath("td[3]").extract()
                land = u"Беларусь"
                oblast = response.xpath("//div[@id='content']/div[@class='item-page']/h2/text()").extract()[0]
                type=1

            else:
                address = item.xpath("td[3]/text()").extract()
                city = item.xpath("td[1]/text()").extract()
                phone = item.xpath("td[4]/text()").extract()
                info = item.xpath("td[2]/text()").extract()
                working_time = u''
                land = u"Казахстан"
                oblast = u""
                type = 2

            office = LagunaItem()
            office['name'] = u''
            office['address'] = address
            office['phone'] = phone
            office['url'] = response.url
            office['city'] = city
            office['country'] = land
            office['oblast'] = oblast
            office['working_time'] = working_time
            office['type'] = type
            yield office
