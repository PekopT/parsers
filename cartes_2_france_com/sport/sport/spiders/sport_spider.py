# -*- coding: utf-8 -*-

import scrapy

from sport.items import SportItem


class SportSpider(scrapy.Spider):
    name = "sport"
    allowed_domains = ["www.cartes-2-france.com"]

    start_urls = (
        'http://www.cartes-2-france.com/activites/75056-paris.php',
    )

    def parse(self, response):
        sports = response.xpath("//*[@id='postal']/tr")
        k = 0
        for sport in sports:
            k +=1
            if k == 1:
                continue

            name = sport.xpath("td[1]/a/text()").extract()
            address = sport.xpath("td[2]/node()").extract()
            item = SportItem()
            item['name'] = name[0]
            item['category'] = u"Les installations sportives"
            item['address'] = address
            yield item

