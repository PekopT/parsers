# -*- coding: utf-8 -*-
import scrapy

from anekdotru.items import AnekdotruItem
class AnekdotSpider(scrapy.Spider):
    name = "anekdot"
    allowed_domains = ["www.anekdot.ru"]
    start_urls = (
        'http://www.anekdot.ru/last/good',
    )

    def parse(self, response):
        topitboxs = response.xpath("//div[@class='wrapper']/div[@class='block-row']/div[contains(@class,'leftcolumn')]/div[@class='topicbox']")
        topitboxs_first = topitboxs[0]
        date = topitboxs_first.xpath("div[@class='subdate']/text()").extract()
        del topitboxs[0]
        for t in topitboxs:
            item = AnekdotruItem()
            item['id'] = t.xpath("div[@class='text']/@id").extract()
            item['text'] = t.xpath("div[@class='text']/text()").extract()
            item['num'] = t.xpath("div[@class='votingbox']/div[@class='num']/text()").extract()
            item['tags'] = t.xpath("div[@class='tags']/a/text()").extract()
            item['author'] = t.xpath("div[@class='votingbox']/div[@class='btn2']/a[@class='link auth']/text()").extract()
            item['url'] = response.url
            item['date'] = date
            yield item

        back = response.xpath("//div[@class='voteresult']/a[1]/@href").extract()[0]
        if back:
            url = response.urljoin(back)
            yield scrapy.Request(url, callback=self.parse)


