#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import scrapy

from yelp.items import YelpItem


class YelpSpider(scrapy.Spider):
    name = "yelp"
    allowed_domains = ["www.yelp.fr"]
    start_urls = [
        "http://www.yelp.fr/search?find_loc=Paris",
    ]

    def parse(self, response):
        pattern = "//div[contains(@class,'all-category-browse-links')]/ul/li/a[contains(@class,'category-browse-anchor')]/@href"
        category_links = response.xpath(pattern)

        for link in category_links:
            link = link.extract()
            url = response.urljoin(link)
            yield scrapy.Request(url, callback=self.parse_subpage)

    def parse_subpage(self, response):
        pattern = "//div[contains(@class,'all-category-browse-links')]/ul/li/a[contains(@class,'category-browse-anchor')]/@href"
        category_links = response.xpath(pattern)

        for link in category_links:
            link = link.extract()
            url = response.urljoin(link)
            yield scrapy.Request(url, callback=self.parse_subpagetest)

    def parse_subpagetest(self, response):
        pattern = "//div[contains(@class,'pagination-links')]/div/div[contains(@class,'arrange_unit')]/a[contains(@class,'next')]/@href"
        next_link = response.xpath(pattern)

        organizations = response.xpath("//li[@class='regular-search-result']")
        for org in organizations:
            org_link = org.xpath("div/div/div/div/div/h3/span/a[@class='biz-name']/@href").extract()
            org_name = org.xpath("div/div/div/div/div/h3/span/a[@class='biz-name']/span/text()").extract()
            org_category = org.xpath("div/div/div/div/div/div/span[@class='category-str-list']/a/text()").extract()
            org_address = org.xpath("div/div/div/address/text()").extract()
            item = YelpItem()
            item['name'] = org_name
            item['category'] = org_category
            item['adress'] = org_address
            yield item

            # org_link = response.urljoin(org_link[0])
            # yield scrapy.Request(org_link, callback=self.parse_org)

        if next_link:
            url = response.urljoin(next_link.extract()[0])
            yield scrapy.Request(url, callback=self.parse_subpagetest)


    def parse_org(self,response):
        item = YelpItem()
        name = response.xpath("//h1/text()").extract()[0]
        categories = response.xpath("//span[@class='category-str-list']/a/text()").extract()
        address = response.xpath("//strong[@class='street-address']/address/span/text()").extract()
        item['name'] = name
        item['category'] = categories
        item['adress'] = address
        yield item

