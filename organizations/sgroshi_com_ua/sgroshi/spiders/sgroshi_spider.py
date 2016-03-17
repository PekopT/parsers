# -*- coding: utf-8 -*-
import scrapy
from sgroshi.items import SgroshiItem


class SgroshiSpider(scrapy.Spider):
    data = []
    working_time_rus = ''
    name = "sgroshi"
    allowed_domains = ["sgroshi.com.ua"]
    start_urls = (
        'http://sgroshi.com.ua/contacts',
    )

    def parse(self, response):
        self.working_time_rus = response.xpath("//h2[1]/span[2]/text()").extract()[0]
        for li in response.xpath("//ul[@class='country']/li"):
            city = li.xpath("h4/span[1]/strong/text()").extract()
            phone = li.xpath("h4/span[2]/text()").extract()
            for otdel in li.xpath("div/div[@id='tabletwo']/descendant::div[@class='item']"):
                # metro = otdel.xpath("img[@class='metro']")
                # if not metro:
                address = otdel.xpath("div[@class='textrow']").extract()[0]
                self.data.append([city, phone, address])

        yield scrapy.Request("http://sgroshi.com.ua/uk/contacts3", callback=self.parse_page)

    def parse_page(self, response):
        c = 0
        working_time_ua = response.xpath("//h2[1]/span[2]/text()").extract()[0]
        for li in response.xpath("//ul[@class='country']/li"):
            city = li.xpath("h4/span[1]/strong/text()").extract()
            # phone = li.xpath("h4/span[2]/text()").extract()
            for otdel in li.xpath("div/div[@id='tabletwo']/descendant::div[@class='item']"):
                # metro = otdel.xpath("img[@class='metro']")
                # if not metro:
                item = SgroshiItem()
                item['address_ua'] = otdel.xpath("div[@class='textrow']").extract()[0]
                item['address'] = self.data[c][2]
                item['city'] = self.data[c][0]
                item['city_ua'] = city
                item['phone'] = self.data[c][1]
                item['url'] = response.url
                item['working_time'] = self.working_time_rus
                item['working_time_ua'] = working_time_ua
                c += 1
                yield item
