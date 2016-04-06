import scrapy
import re

from viamichelin.pipelines import HotelPipeline, RestaurantPipeline
from viamichelin.items import HotelItem, RestaurantItem


class ViamichelinHotelSpider(scrapy.Spider):
    counter = 0
    name = "viamichelinhotel"
    allowed_domains = ["www.viamichelin.fr"]

    pipeline = set([
        HotelPipeline,
    ])

    start_urls = (
        'http://www.viamichelin.fr/web/Hotels/Hotels-Paris-75000-Ville_de_Paris-France?strLocid=31NDJ2dDMxMGNORGd1T0RVMk9EUT1jTWk0ek5URXdOdz09&page=1',
    )

    def parse(self, response):
        total = response.xpath("//p[@class='pagination-first-line']/a[last()]/@data-pagination")
        if total:
            total = total.extract()[0]
            total = int(total) + 1
        for page in range(1, total):
            url = 'http://www.viamichelin.fr/web/Hotels/Hotels-Paris-75000-Ville_de_Paris-France?strLocid=31NDJ2dDMxMGNORGd1T0RVMk9EUT1jTWk0ek5URXdOdz09&page={0}'.format(
                page)
            yield scrapy.Request(url, callback=self.parse_page)

    def parse_page(self, response):
        hotels = response.xpath("//ul[@class='poilist']/li")
        for hotel in hotels:
            name = hotel.xpath("div[contains(@class,'poi-item-name')]/a/text()")
            address = hotel.xpath("div[contains(@class,'poi-item-address')]/text()")
            address_title = hotel.xpath("div[contains(@class,'poi-item-address')]/@title")
            item = HotelItem()
            item['name'] = name.extract()
            item['category'] = u"Hotel"
            item['address'] = address.extract()
            item['address_title'] = address_title.extract()
            yield item


class ViamichelinRestaurantSpider(scrapy.Spider):
    counter = 0
    name = "viamichelinrestaurant"
    allowed_domains = ["www.viamichelin.fr"]

    pipeline = set([
        RestaurantPipeline,
    ])

    start_urls = (
        'http://www.viamichelin.fr/web/Recherche_Restaurants/Restaurants-Paris-75000-Ville_de_Paris-France?strLocid=31NDJ2dDMxMGNORGd1T0RVMk9EUT1jTWk0ek5URXdOdz09&page=1',
    )

    def parse(self, response):
        total = response.xpath("//p[@class='pagination-first-line']/a[last()]/@data-pagination")
        if total:
            total = total.extract()[0]
            total = int(total) + 1
        for page in range(1, total):
            url = 'http://www.viamichelin.fr/web/Recherche_Restaurants/Restaurants-Paris-75000-Ville_de_Paris-France?strLocid=31NDJ2dDMxMGNORGd1T0RVMk9EUT1jTWk0ek5URXdOdz09&page={0}'.format(
                page)
            yield scrapy.Request(url, callback=self.parse_page)

    def parse_page(self, response):
        hotels = response.xpath("//ul[@class='poilist']/li")
        for hotel in hotels:
            name = hotel.xpath("div[contains(@class,'poi-item-name')]/a/text()")
            address = hotel.xpath("div[contains(@class,'poi-item-address')]/text()")
            address_title = hotel.xpath("div[contains(@class,'poi-item-address')]/@title")
            item = RestaurantItem()
            item['name'] = name.extract()
            item['category'] = u"Hotel"
            item['address'] = address.extract()
            item['address_title'] = address_title.extract()
            yield item
