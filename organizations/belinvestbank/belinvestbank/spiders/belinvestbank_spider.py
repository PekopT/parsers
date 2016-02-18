# -*- coding: utf-8 -*-
from belinvestbank.items import BelinvestbankAtmItem, BelinvestbankOfficeItem
from belinvestbank.pipelines import BelinvestbankAtmPipeline, BelinvestbankInfoPipeline, BelinvestbankOfficePipeline
from urlparse import urlparse

__author__ = 'PekopT'

from sys import stdout

import scrapy
from codecs import getwriter

sout = getwriter("utf8")(stdout)


class BelinvestbankXmlMixin(object):
    def parse_item(self, item, region, name, response):
        atm = BelinvestbankAtmItem()
        atm['region'] = region
        add_address = item.xpath('div[@class="addres"]/strong/text()').extract()
        info = item.xpath('div[@class="addres"]/b/text() | div[@class="addres"]/text()').extract()
        info = [x.strip() for x in info if
                x.strip()]
        try:
            time_index = info.index(u'Время работы:')
            atm['time'] = info[time_index + 1].strip()
        except Exception:
            atm['time'] = False

        try:
            info.index(u'Взнос наличных:')
            atm['accept'] = True
        except Exception:
            atm['accept'] = False

        try:
            curr_index = info.index(u'Валюта:')
            curr = info[curr_index + 1]
            atm_cur = []
            for cur in curr.split(','):
                if cur.strip() == u'Бел. Рубли':
                    atm_cur.append(u'byr')
                if cur.strip() == u'EUR':
                    atm_cur.append(u'eur')
                if cur.strip() == u'USD':
                    atm_cur.append(u'usd')

            if atm_cur:
                atm['curr'] = atm_cur
        except Exception:
            atm['curr'] = []

        atm['name'] = name
        atm['add_address'] = add_address
        atm['url'] = response.url
        atm['info'] = info
        return atm


class BelinvestbankAtmSpider(scrapy.Spider, BelinvestbankXmlMixin):
    name = "BelinvestbankAtms"
    allowed_domains = ["www.belinvestbank.by"]
    start_urls = [
        "http://www.belinvestbank.by/atm/",
    ]

    pipeline = set([
        BelinvestbankAtmPipeline,
    ])

    def parse(self, response):
        for href in response.xpath('//div[@class="region"]/p/a/@href'):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_atm_page)

    def parse_atm_page(self, response):
        region = response.xpath('//div[@class="plashka"]/ul/li/span/text()').extract()[0].strip()
        for item in response.xpath('//div[@class="list"]/div[@class="item"]'):
            item_name = item.xpath('div[@class="name a"]/a/span/text()').extract()[0]

            if item_name.find(u'Банкомат') != -1:
                atm = self.parse_item(item, region, item_name, response)
                yield atm


class BelinvestbankInfoSpider(scrapy.Spider, BelinvestbankXmlMixin):
    name = "BelinvestbankInfos"
    allowed_domains = ["www.belinvestbank.by"]
    start_urls = [
        "http://www.belinvestbank.by/atm/",
    ]

    pipeline = set([
        BelinvestbankInfoPipeline,
    ])

    def parse(self, response):
        for href in response.xpath('//div[@class="region"]/p/a/@href'):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_atm_page)

    def parse_atm_page(self, response):
        region = response.xpath('//div[@class="plashka"]/ul/li/span/text()').extract()[0].strip()
        for item in response.xpath('//div[@class="list"]/div[@class="item"]'):
            item_name = item.xpath('div[@class="name a"]/a/span/text()').extract()[0]

            if item_name.find(u'Инфокиоск') != -1:
                atm = self.parse_item(item, region, item_name, response)
                yield atm


class BelinvestbankOfficeSpider(scrapy.Spider):
    name = "BelinvestbankOffices"
    allowed_domains = ["www.belinvestbank.by"]
    start_urls = [
        "http://www.belinvestbank.by/geo/",
    ]

    pipeline = set([
        BelinvestbankOfficePipeline,
    ])

    def parse(self, response):
        for href in response.xpath('//div[@class="region"]/p/a/@href'):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_atm_page)

    def parse_atm_page(self, response):
        parsed_url = urlparse(response.url)
        path = parsed_url.path.replace('/geo/', '')+'?'+parsed_url.query
        region = response.xpath('//div[@class="plashka"]/ul/li/a[@href = "%s"]/text() | //div[@class="plashka"]/ul/li[@class="a"]/span/text()' % path).extract()[0].strip()
        for item in response.xpath('//div[@class="list"]/div[@class="item"]'):
            item_name = item.xpath('div[@class="name a"]/a/span/text()').extract()[0].strip()
            office = BelinvestbankOfficeItem()
            office['name'] = item_name
            office['url'] = response.url
            office['address'] = item.xpath('div[@class="addres"]/strong/text()').extract()[0].strip()
            office['phones'] = item.xpath('div[@class="item_block"]//tr/td[1]/strong/text()').extract()
            office['region'] = region
            yield office
