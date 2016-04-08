# -*- coding: utf-8 -*-

import scrapy

from viamichelin.pipelines import ViamichelinPipeline
from viamichelin.items import ViamichelinItem

class ViamichelinSpider(scrapy.Spider):
    name = "viamichelin"
    allowed_domains = ["www.viamichelin.fr"]
    start_urls = (
        'http://www.viamichelin.fr',
    )

    pipeline = set([
        ViamichelinPipeline,
    ])

    def parse(self,response):
        hotel_url = 'http://www.viamichelin.fr/web/Hotels/Hotels-Paris-75000-Ville_de_Paris-France?strLocid=31NDJ2dDMxMGNORGd1T0RVMk9EUT1jTWk0ek5URXdOdz09&page=1'
        restoraunt_url = 'http://www.viamichelin.fr/web/Recherche_Restaurants/Restaurants-Paris-75000-Ville_de_Paris-France?strLocid=31NDJ2dDMxMGNORGd1T0RVMk9EUT1jTWk0ek5URXdOdz09&page=1'
        yield scrapy.Request(hotel_url, callback=self.parse_hotels)
        yield scrapy.Request(restoraunt_url, callback=self.parse_restoraunt)

    def parse_hotels(self,response):
        total = response.xpath("//p[@class='pagination-first-line']/a[last()]/@data-pagination")
        if total:
            total = total.extract()[0]
            total = int(total) + 1
        for page in range(1, total):
            url = 'http://www.viamichelin.fr/web/Hotels/Hotels-Paris-75000-Ville_de_Paris-France?strLocid=31NDJ2dDMxMGNORGd1T0RVMk9EUT1jTWk0ek5URXdOdz09&page={0}'.format(
                page)
            yield scrapy.Request(url, callback=self.parse_hotel_page)

    def parse_hotel_page(self, response):
        hotels = response.xpath("//ul[@class='poilist']/li")
        for hotel in hotels:
            name = hotel.xpath("div[contains(@class,'poi-item-name')]/a/text()")
            address = hotel.xpath("div[contains(@class,'poi-item-address')]/text()")
            address_title = hotel.xpath("div[contains(@class,'poi-item-address')]/@title")
            item = ViamichelinItem()
            item['name'] = name.extract()
            item['category'] = u"Hotel"
            item['address'] = address.extract()
            item['address_title'] = address_title.extract()
            yield item

    def parse_restoraunt(self, response):
        total = response.xpath("//p[@class='pagination-first-line']/a[last()]/@data-pagination")
        if total:
            total = total.extract()[0]
            total = int(total) + 1
        for page in range(1, total):
            url = 'http://www.viamichelin.fr/web/Recherche_Restaurants/Restaurants-Paris-75000-Ville_de_Paris-France?strLocid=31NDJ2dDMxMGNORGd1T0RVMk9EUT1jTWk0ek5URXdOdz09&page={0}'.format(
                page)
            yield scrapy.Request(url, callback=self.parse_restoraunt_page)

    def parse_restoraunt_page(self, response):
        restoraunts = response.xpath("//ul[@class='poilist']/li")
        for rest in restoraunts:
            name = rest.xpath("div[contains(@class,'poi-item-name')]/a/text()")
            address = rest.xpath("div[contains(@class,'poi-item-address')]/text()")
            address_title = rest.xpath("div[contains(@class,'poi-item-address')]/@title")
            item = ViamichelinItem()
            item['name'] = name.extract()
            item['category'] = u"restaurant"
            item['address'] = address.extract()
            item['address_title'] = address_title.extract()
            yield item

