# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import FormRequest
from sgroshi.items import SgroshiItem

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:28.0) Gecko/20100101 Firefox/28.0',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest'
}


class SgroshiSpider(scrapy.Spider):
    data = []
    working_time_rus = ''
    name = "sgroshi"
    allowed_domains = ["sgroshi.com.ua"]
    start_urls = (
        'http://sgroshi.com.ua/contacts',
    )

    def parse(self, response):

        yield scrapy.Request("http://sgroshi.com.ua/amap_req.php?lng=ru", body='action=get_table_cities_departments',
                             method='POST', headers=headers, callback=self.parse_category)

    def parse_category(self, response):
        cities = response.xpath("//div[@class='office-city-block']")
        for city_block in cities:
            city_info = city_block.xpath("div[@class='office-city']/a/text()")
            city = city_info.extract()
            if city:
                city = city[0]

            for otdel in city_block.xpath(
                    "div[@class='office-city-body']/div[@class='office-table']/div[@class='office-table-tr']"):
                address_info = otdel.xpath("div/div/span[@itemprop='address']")
                if address_info:
                    street = address_info.xpath("b[@itemprop='streetAddress']/text()").extract()
                    street = street[0]
                    address = street

                phone = otdel.xpath("div/div/span[@itemprop='telephone']/b/text()").extract()
                times_info = otdel.xpath("div/div/span/time/@datetime")
                address_add_info = otdel.xpath("div[@itemprop='description']/p/text()").extract()

                if address_add_info:
                    address_add = ''.join([adr for adr in address_add_info]).strip()
                else:
                    address_add = ''


                working_time = ','.join([time for time in times_info.extract()])

                self.data.append([city, phone, address, working_time, address_add])


        yield scrapy.Request("http://sgroshi.com.ua/amap_req.php?lng=ua", body='action=get_table_cities_departments',
                             method='POST', headers=headers, callback=self.parse_page)


    def parse_page(self, response):
        c = 0
        cities = response.xpath("//div[@class='office-city-block']")
        for city_block in cities:
            city_info = city_block.xpath("div[@class='office-city']/a/text()")
            city_ua = city_info.extract()
            if city_ua:
                city_ua = city_ua[0]

            for otdel in city_block.xpath(
                    "div[@class='office-city-body']/div[@class='office-table']/div[@class='office-table-tr']"):

                address_info = otdel.xpath("div/div/span[@itemprop='address']")
                if address_info:
                    street = address_info.xpath("b[@itemprop='streetAddress']/text()").extract()
                    street = street[0]
                    address = street

                item = SgroshiItem()
                item['address_ua'] = address
                item['address'] = self.data[c][2]
                item['city'] = self.data[c][0]
                item['city_ua'] = city_ua
                item['phone'] = self.data[c][1]
                item['url'] = response.url
                item['working_time'] = self.data[c][3]
                item['address_add_ru'] = self.data[c][4]

                address_add_info = otdel.xpath("div[@itemprop='description']/p/text()").extract()

                if address_add_info:
                    address_add_ua = ''.join([adr for adr in address_add_info]).strip()
                else:
                    address_add_ua = ''
                item['address_add_ua'] = address_add_ua
                c += 1
                yield item