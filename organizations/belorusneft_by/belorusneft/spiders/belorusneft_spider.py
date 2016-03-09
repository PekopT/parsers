#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import scrapy

from belorusneft.items import BelorusneftItem


class BelorusneftSpider(scrapy.Spider):
    name = "belorusneft"
    allowed_domains = ["www.belorusneft.by"]
    start_urls = [
        "http://www.belorusneft.by/beloil-map/allsearchres?lang=ru&country=by&brand=&number=&area=&district=&road=&town=&fuels=&services=&paymentmethods=&sm=&fm=&pm=&operation=&actions=",
    ]

    def parse(self, response):
        jsonresponse = json.loads(response.body_as_unicode())
        for resp in jsonresponse['stations']:
            item = BelorusneftItem()
            item['address'] = resp['address']
            item['phone'] = resp['phone']
            item['fuels'] = resp['fuels']
            item['services'] = resp['services']
            item['latitude'] = resp['latitude']
            item['longitude'] = resp['longitude']
            yield item