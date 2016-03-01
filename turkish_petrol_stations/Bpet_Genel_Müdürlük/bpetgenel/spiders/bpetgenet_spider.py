# -*- coding: utf-8 -*-

import scrapy

from bpetgenel.items import BpetgenelItem

class BpetgenetSpider(scrapy.Spider):
    name = "bpetgenet"
    allowed_domains = ["www.bpet.com.tr"]
    start_urls = (
        'http://www.bpet.com.tr/tr/bayi-agi',
    )

    def __init__(self):
        self.count_item = 0

    def parse(self,response):
        cities = response.xpath("//select/option/@value").extract()
        items = response.xpath("//select/option")
        for item in items:
            city_id = item.xpath('@value').extract()
            city = item.xpath('text()').extract()
            if city_id:
                url = "http://www.bpet.com.tr/tr/iller/" + city_id[0]
                yield scrapy.Request(url,callback=self.parse_page,meta={'city':city[0]})

    def parse_page(self,response):
        links = response.xpath("//div[@class='span8']/ul[@class='listarrow']/li/a/@href").extract()

        for link in links:
            url = response.urljoin(link)
            city_id = response.meta['city']
            yield scrapy.Request(url,callback=self.parse_page_detail,meta={'city':city_id})

    def parse_page_detail(self,response):
         self.count_item +=1
         item = BpetgenelItem()
         item['name'] = response.xpath('//div/div[@class="row-fluid"]/div[@class="span8"]/h2').extract()[0]
         item['address'] = response.xpath('//div[@class="span12"]/div/div[@class="row-fluid"]/div[@class="span8"]/p[2]/text()').extract()[0]
         item['phone'] = response.xpath('//div[@class="span12"]/div/div[@class="row-fluid"]/div[@class="span8"]/p[3]/text()').extract()[0]
         item['fax'] = response.xpath('//div[@class="span12"]/div/div[@class="row-fluid"]/div[@class="span8"]/p[3]/text()').extract()[0]
         item['latitude'] = response.xpath('//div[@class="span12"]/div/div[@class="row-fluid"]/div[@class="span8"]/p[4]/text()').extract()[0]
         item['longitude'] = response.xpath('//div[@class="span12"]/div/div[@class="row-fluid"]/div[@class="span8"]/p[5]/text()').extract()[0]
         item['url'] = response.url
         item['city'] = response.meta['city']
         yield item

