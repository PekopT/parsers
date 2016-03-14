# -*- coding: utf-8 -*-
import re
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
        anekdot_rates_raw = response.xpath("//script[re:test(text(),'anekdot_rate')]").extract()[0]
        m = re.search(u'anekdot_rates(.)+\;', anekdot_rates_raw)
        ak_rates = m.group(0)
        ak_rates = ak_rates.replace(u"anekdot_rates=[", '')[1:-3]
        ak_rates_data = ak_rates.split(u"','")

        ak_rates_dict = {}
        for k in ak_rates_data:
            key_list = k.split(',')
            ak_rates_dict[key_list[0]] = key_list[1:]


        for t in topitboxs:
            item = AnekdotruItem()
            id = t.xpath("div[@class='text']/@id").extract()[0]
            id = re.sub(u'\D', '', id)
            item['id'] = t.xpath("div[@class='text']/@id").extract()
            item['text'] = t.xpath("div[@class='text']").extract()
            item['num'] = t.xpath("div[@class='votingbox']/div[@class='num']/text()").extract()
            item['tags'] = t.xpath("div[@class='tags']/a/text()").extract()
            item['author'] = t.xpath("div[@class='votingbox']/div[@class='btn2']/a[@class='link auth']/text()").extract()
            item['url'] = response.url
            item['date'] = date
            item['rating'] = ak_rates_dict[id]
            yield item

        back = response.xpath("//div[@class='voteresult']/a[1]/@href").extract()[0]
        if back:
            url = response.urljoin(back)
            yield scrapy.Request(url, callback=self.parse)


