# -*- coding: utf-8 -*-
import scrapy
import json
import re

from biletix.items import EventItem, EventGroupItem, MekanItem, PersonaItem
from biletix.pipelines import EventPipeline, EventGroupPipeline, MekanPipeline, PersonaPipeline

# COOKIES = {'BXID': 'AAAAAAU7lWrMThR3h0fEGr+GuVZciZ51Fszj2PFmcdM1fpVqtA=='}


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:28.0) Gecko/20100101 Firefox/28.0',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
}

class BiletEventGroupSpider(scrapy.Spider):
    name = "biletixgroup"
    allowed_domains = ["www.biletix.com"]
    start_urls = (
        'http://www.biletix.com',
    )
    cookies = {}

    pipeline = set([
        EventGroupPipeline,
    ])

    def parse(self, response):
        content = response.body
        m = re.search("BXID.+\;?",content)
        cookies = {}
        if m:
            test = m.group(0)
            pos = test.find(';')
            cookies_info = test[:pos].replace("BXID=","")
            self.cookies = {"BXID": cookies_info}

        urls = [
            "http://www.biletix.com/solr/en/select/?start=0&rows=10000&q=category:MUSIC&qt=standard&fq=end%3A%5B2016-03-29T00%3A00%3A00Z%20TO%202018-04-02T00%3A00%3A00Z%2B1DAY%5D&sort=vote%20desc,start%20asc&&wt=json",
            "http://www.biletix.com/solr/tr/select/?start=0&rows=10000&q=category:SPORT&qt=standard&fq=end%3A%5B2016-03-31T00%3A00%3A00Z%20TO%202018-04-01T00%3A00%3A00Z%2B1DAY%5D&sort=vote%20desc,start%20asc&&wt=json",
            "http://www.biletix.com/solr/tr/select/?start=0&rows=10000&q=category:ART&qt=standard&fq=end%3A%5B2016-04-03T00%3A00%3A00Z%20TO%202018-04-04T00%3A00%3A00Z%2B1DAY%5D&sort=vote%20desc,start%20asc&&wt=json",
            "http://www.biletix.com/solr/tr/select/?start=0&rows=10000&q=category:FAMILY&qt=standard&fq=end%3A%5B2016-04-03T00%3A00%3A00Z%20TO%202018-04-04T00%3A00%3A00Z%2B1DAY%5D&sort=vote%20desc,start%20asc&&wt=json",
            "http://www.biletix.com/solr/tr/select/?start=0&rows=10000&q=category:OTHER&qt=standard&fq=end%3A%5B2016-04-03T00%3A00%3A00Z%20TO%202018-04-04T00%3A00%3A00Z%2B1DAY%5D&sort=vote%20desc,start%20asc&&wt=json"
        ]
        for url in urls:
            yield scrapy.Request(url, headers=HEADERS, cookies=self.cookies, callback=self.parse_category)

    def parse_category(self, response):
        jsonresponse = json.loads(response.body_as_unicode())

        for resp in jsonresponse['response']['docs']:
            if u"group" in resp["type"]:
                url = "http://www.biletix.com/{0}/{1}/{2}/tr"
                url = url.format('etkinlik-grup', resp["id"], resp["region"])
                meta_info = {'category': resp['category'], 'subcategory': resp['subcategory'], 'id': resp['id']}
                yield scrapy.Request(url, cookies=self.cookies, meta=meta_info,
                                     callback=self.parse_detail)

    def parse_detail(self, response):
        category = response.meta['category']
        id = response.meta['id']
        title = response.xpath("//h1[@itemprop='name']/text()")
        init_date = response.xpath("//h2/span[@itemprop='startDate']/@content")
        end_date = response.xpath("//h2/span[@itemprop='endDate']/@content")
        images = response.xpath("//div[@class='eventGroupImage']/img/@src")
        description = response.xpath("//p[@itemprop='description']/node()")
        place = response.xpath("//div[contains(@class,'eventname')]/ul/li/span[@itemprop='addressLocality']/text()")
        performers = response.xpath("//span[@itemprop='performer']")
        participants = []
        for perform in performers:
            p_name = perform.xpath("span[@itemprop='name']/a/@href").extract()
            participants.append(p_name[0].strip())

        item = EventGroupItem()

        item['id'] = id
        item['title'] = title.extract()
        item['url'] = response.url
        item['participants'] = participants
        item['init_date'] = init_date.extract()
        item['end_date'] = end_date.extract()
        item['description'] = description.extract()
        item['place'] = place.extract()
        item['category'] = category
        item['images'] = images.extract()
        yield item


class MekanSpider(scrapy.Spider):
    name = "biletixmekan"
    allowed_domains = ["www.biletix.com"]
    start_urls = (
        'http://www.biletix.com',
    )
    mekan_data = []
    cookies = {}

    pipeline = set([
        MekanPipeline,
    ])

    def parse(self, response):
        content = response.body
        m = re.search("BXID.+\;?",content)
        if m:
            test = m.group(0)
            pos = test.find(';')
            cookies_info = test[:pos].replace("BXID=","")
            self.cookies = {"BXID": cookies_info}


        urls = [
            "http://www.biletix.com/solr/en/select/?start=0&rows=10000&q=category:MUSIC&qt=standard&fq=end%3A%5B2016-03-29T00%3A00%3A00Z%20TO%202018-04-02T00%3A00%3A00Z%2B1DAY%5D&sort=vote%20desc,start%20asc&&wt=json",
            "http://www.biletix.com/solr/tr/select/?start=0&rows=10000&q=category:SPORT&qt=standard&fq=end%3A%5B2016-03-31T00%3A00%3A00Z%20TO%202018-04-01T00%3A00%3A00Z%2B1DAY%5D&sort=vote%20desc,start%20asc&&wt=json",
            "http://www.biletix.com/solr/tr/select/?start=0&rows=10000&q=category:ART&qt=standard&fq=end%3A%5B2016-04-03T00%3A00%3A00Z%20TO%202018-04-04T00%3A00%3A00Z%2B1DAY%5D&sort=vote%20desc,start%20asc&&wt=json",
            "http://www.biletix.com/solr/tr/select/?start=0&rows=10000&q=category:FAMILY&qt=standard&fq=end%3A%5B2016-04-03T00%3A00%3A00Z%20TO%202018-04-04T00%3A00%3A00Z%2B1DAY%5D&sort=vote%20desc,start%20asc&&wt=json",
            "http://www.biletix.com/solr/tr/select/?start=0&rows=10000&q=category:OTHER&qt=standard&fq=end%3A%5B2016-04-03T00%3A00%3A00Z%20TO%202018-04-04T00%3A00%3A00Z%2B1DAY%5D&sort=vote%20desc,start%20asc&&wt=json"
        ]
        for url in urls:
            yield scrapy.Request(url, headers=HEADERS, cookies=self.cookies, callback=self.parse_category)

    def parse_category(self, response):
        jsonresponse = json.loads(response.body_as_unicode())

        for resp in jsonresponse['response']['docs']:
            if u"group" in resp["type"]:
                url = "http://www.biletix.com/{0}/{1}/{2}/tr"
                url = url.format('etkinlik-grup', resp["id"], resp["region"])
                meta_info = {'category': resp['category'], 'subcategory': resp['subcategory'], 'id': resp['id']}
                yield scrapy.Request(url, cookies=self.cookies, meta=meta_info, callback=self.parse_page)

    def parse_page(self, response):
        performers = response.xpath("//div[@itemprop='location']")
        participants = []
        for perform in performers:
            p_name = perform.xpath("a[@itemprop='url']/@href").extract()[0].strip()
            if p_name not in self.mekan_data:
                self.mekan_data.append(p_name)
                participants.append(p_name)
                url = response.urljoin(p_name)
                yield scrapy.Request(url, cookies=self.cookies,
                                     callback=self.parse_mekan)

    def parse_mekan(self, response):
        title = response.xpath("//h1[@itemprop='name']/text()")
        description = response.xpath("//p[@itemprop='description']/node()")
        images = response.xpath("//div[@id='vi_header']/div/img/@src")
        performers = response.xpath("//div[@id='venueresultlists']/div/div/div/span/span[@itemprop='name']/a/@href")
        place = response.xpath("//*[@id='vi_header']/div/ul/li/span[@itemprop='addressLocality']/text()")
        item = MekanItem()
        item['title'] = title.extract()
        item['description'] = description.extract()
        item['projects'] = performers.extract()
        item['images'] = images.extract()
        item['place'] = place.extract()
        item['url'] = response.url
        yield item


class BiletixEventSpider(scrapy.Spider):
    name = "biletixevent"
    allowed_domains = ["www.biletix.com"]
    start_urls = (
        'http://www.biletix.com',
    )

    cookies = {}

    pipeline = set([
        EventPipeline,
    ])

    def parse(self,response):
        content = response.body
        m = re.search("BXID.+\;?",content)
        if m:
            test = m.group(0)
            pos = test.find(';')
            cookies_info = test[:pos].replace("BXID=","")
            self.cookies = {"BXID": cookies_info}
        urls = [
            "http://www.biletix.com/solr/en/select/?start=0&rows=10000&q=category:MUSIC&qt=standard&fq=end%3A%5B2016-03-29T00%3A00%3A00Z%20TO%202018-04-02T00%3A00%3A00Z%2B1DAY%5D&sort=vote%20desc,start%20asc&&wt=json",
            "http://www.biletix.com/solr/tr/select/?start=0&rows=10000&q=category:SPORT&qt=standard&fq=end%3A%5B2016-03-31T00%3A00%3A00Z%20TO%202018-04-01T00%3A00%3A00Z%2B1DAY%5D&sort=vote%20desc,start%20asc&&wt=json",
            "http://www.biletix.com/solr/tr/select/?start=0&rows=10000&q=category:ART&qt=standard&fq=end%3A%5B2016-04-03T00%3A00%3A00Z%20TO%202018-04-04T00%3A00%3A00Z%2B1DAY%5D&sort=vote%20desc,start%20asc&&wt=json",
            "http://www.biletix.com/solr/tr/select/?start=0&rows=10000&q=category:FAMILY&qt=standard&fq=end%3A%5B2016-04-03T00%3A00%3A00Z%20TO%202018-04-04T00%3A00%3A00Z%2B1DAY%5D&sort=vote%20desc,start%20asc&&wt=json",
            "http://www.biletix.com/solr/tr/select/?start=0&rows=10000&q=category:OTHER&qt=standard&fq=end%3A%5B2016-04-03T00%3A00%3A00Z%20TO%202018-04-04T00%3A00%3A00Z%2B1DAY%5D&sort=vote%20desc,start%20asc&&wt=json"
        ]
        for url in urls:
            yield scrapy.Request(url, headers=HEADERS, cookies=self.cookies, callback=self.parse_category)

    def parse_category(self, response):
        jsonresponse = json.loads(response.body_as_unicode())

        for resp in jsonresponse['response']['docs']:
            if u"event" in resp["type"]:
                url = "http://www.biletix.com/{0}/{1}/{2}/tr"
                url = url.format('etkinlik', resp["id"], resp["region"])
                meta_info = {'category': resp['category'], 'subcategory': resp['subcategory'], 'id': resp['id']}
                yield scrapy.Request(url, cookies=self.cookies, meta=meta_info,
                                     callback=self.parse_page)
                break

    def parse_page(self, response):
        title = response.xpath("//*[@id='eventnameh1']/span/text()")
        init_date = response.xpath("//*[@id='eventdatefields']/h2/@content")
        images = response.xpath("//div[@class='thumbnails']/ul/li/a[1]/@href")
        description = response.xpath("//p[@itemprop='description']/node()")
        itemscope = response.xpath("//div[@id='tab1']/div/div[@class='epcontent']/div[@itemscope='itemscope']")
        prices_data = []
        for scope in itemscope:
            comment = scope.xpath("span[@itemprop='name']/text()").extract()
            price= scope.xpath("span[@itemprop='price']/text()").extract()
            prices_data.append({'comment':comment[0].strip(), 'price': price[0].strip()})
        # price = response.xpath("//div[@id='tab1']/div/div[@class='epcontent']/div/span[@itemprop='price']")
        item = EventItem()
        item['title'] = title.extract()
        item['init_date'] = init_date.extract()
        item['description'] = description.extract()
        item['url'] = response.url
        item['price'] = prices_data
        item['images'] = images.extract()
        item['id'] = response.meta['id']
        item['category'] = response.meta['category']
        yield item


class PersonaSpider(scrapy.Spider):
    name = "biletixpersona"
    allowed_domains = ["www.biletix.com"]
    start_urls = (
        'http://www.biletix.com',
    )
    cookies = {}

    pipeline = set([
        PersonaPipeline,
    ])

    def parse(self, response):
        content = response.body
        m = re.search("BXID.+\;?",content)
        if m:
            test = m.group(0)
            pos = test.find(';')
            cookies_info = test[:pos].replace("BXID=","")
            self.cookies = {"BXID": cookies_info}

        urls = [
            "http://www.biletix.com/solr/en/select/?start=0&rows=10000&q=category:MUSIC&qt=standard&fq=end%3A%5B2016-03-29T00%3A00%3A00Z%20TO%202018-04-02T00%3A00%3A00Z%2B1DAY%5D&sort=vote%20desc,start%20asc&&wt=json",
            "http://www.biletix.com/solr/tr/select/?start=0&rows=10000&q=category:ART&qt=standard&fq=end%3A%5B2016-04-03T00%3A00%3A00Z%20TO%202018-04-04T00%3A00%3A00Z%2B1DAY%5D&sort=vote%20desc,start%20asc&&wt=json",
            "http://www.biletix.com/solr/tr/select/?start=0&rows=10000&q=category:FAMILY&qt=standard&fq=end%3A%5B2016-04-03T00%3A00%3A00Z%20TO%202018-04-04T00%3A00%3A00Z%2B1DAY%5D&sort=vote%20desc,start%20asc&&wt=json",
            "http://www.biletix.com/solr/tr/select/?start=0&rows=10000&q=category:OTHER&qt=standard&fq=end%3A%5B2016-04-03T00%3A00%3A00Z%20TO%202018-04-04T00%3A00%3A00Z%2B1DAY%5D&sort=vote%20desc,start%20asc&&wt=json"
        ]

        for url in urls:
            yield scrapy.Request(url, headers=HEADERS, cookies=self.cookies, callback=self.parse_category)


    def parse_category(self, response):
        jsonresponse = json.loads(response.body_as_unicode())

        for resp in jsonresponse['response']['docs']:
            if u"event" in resp["type"]:
                url = "http://www.biletix.com/{0}/{1}/{2}/tr"
                url = url.format('etkinlik', resp["id"], resp["region"])
                meta_info = {'category': resp['category'], 'subcategory': resp['subcategory'], 'id': resp['id']}
                yield scrapy.Request(url, cookies=self.cookies, meta=meta_info,
                                     callback=self.parse_detail)


    def parse_detail(self, response):
        title = response.xpath("//*[@id='eventnameh1']/span/text()")
        socials = []
        sl_id_info = response.xpath(
            "//div[@id='ep_video_photo']/div[@class='contenttabs']/ul[@class='tabs']/li/a[re:test(text(),'Resmi\s*Site')]/@href")

        if sl_id_info:
            sl_id = sl_id_info.extract()[0].strip()[1:]
            social_info = response.xpath(
                "//div[@id='ep_video_photo']/div/div/div/div/div[@id='%s']/table/tr[1]/td/table/tr/td/a" % sl_id)

            for soc in social_info:
                s_url = soc.xpath('@href').extract()[0]
                s_title = soc.xpath('@title').extract()[0]
                socials.append({'url': s_url, 'title': s_title})

        item = PersonaItem()
        item['id'] = response.meta['id']
        item['category'] = response.meta['category']
        item['subcategory'] = response.meta['subcategory']
        item['title'] = title.extract()
        item['social'] = socials
        item['url'] = response.url
        yield item


class BiletixSpider(scrapy.Spider):
    counter = 0
    name = "biletix"
    allowed_domains = ["www.biletix.com"]
    start_urls = (
        'http://www.biletix.com',
    )

    pipeline = set([])

    def parse(self, response):
        content = response.body
        m = re.search("BXID.+\;?",content)
        cookies = {}
        if m:
            test = m.group(0)
            pos = test.find(';')
            cookies_info = test[:pos].replace("BXID=","")
            cookies = {"BXID": cookies_info}

        yield scrapy.Request("http://www.biletix.com/category/MUSIC/ISTANBUL/tr", cookies=cookies, meta={'cookiejar': 1},
                              callback=self.parse_test)

    def parse_test(self, response):
        print response.body

        #
        # urls = [
        #     "http://www.biletix.com/solr/en/select/?start=0&rows=10000&q=category:MUSIC&qt=standard&fq=end%3A%5B2016-03-29T00%3A00%3A00Z%20TO%202018-04-02T00%3A00%3A00Z%2B1DAY%5D&sort=vote%20desc,start%20asc&&wt=json",
        #     "http://www.biletix.com/solr/tr/select/?start=0&rows=10000&q=category:SPORT&qt=standard&fq=end%3A%5B2016-03-31T00%3A00%3A00Z%20TO%202018-04-01T00%3A00%3A00Z%2B1DAY%5D&sort=vote%20desc,start%20asc&&wt=json",
        #     "http://www.biletix.com/solr/tr/select/?start=0&rows=10000&q=category:ART&qt=standard&fq=end%3A%5B2016-04-03T00%3A00%3A00Z%20TO%202018-04-04T00%3A00%3A00Z%2B1DAY%5D&sort=vote%20desc,start%20asc&&wt=json",
        #     "http://www.biletix.com/solr/tr/select/?start=0&rows=10000&q=category:FAMILY&qt=standard&fq=end%3A%5B2016-04-03T00%3A00%3A00Z%20TO%202018-04-04T00%3A00%3A00Z%2B1DAY%5D&sort=vote%20desc,start%20asc&&wt=json",
        #     "http://www.biletix.com/solr/tr/select/?start=0&rows=10000&q=category:OTHER&qt=standard&fq=end%3A%5B2016-04-03T00%3A00%3A00Z%20TO%202018-04-04T00%3A00%3A00Z%2B1DAY%5D&sort=vote%20desc,start%20asc&&wt=json"
        # ]
        #
        # for url in urls:
        #     yield scrapy.Request(url, headers={
        #         'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:28.0) Gecko/20100101 Firefox/28.0',
        #         'Accept': 'application/json, text/javascript, */*; q=0.01',
        #         'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        #         'X-Requested-With': 'XMLHttpRequest',
        #     }, cookies={'BXID': 'AAAAAAU7lWrMThR3h0fEGr+GuVZciZ51Fszj2PFmcdM1fpVqtA=='}, callback=self.parse_page)

        # def parse_page(self, response):
        #     jsonresponse = json.loads(response.body_as_unicode())
        #
        #     for resp in jsonresponse['response']['docs']:
        #         url = "http://www.biletix.com/{0}/{1}/{2}/tr"
        #         url = url.format('etkinlik', resp["id"], resp["region"])
        #         if u"event" in resp['type']:
        #             self.counter += 1
        #             print self.counter
        #             # yield scrapy.Request(url,callback=self.parse_detail)
        #
        # def parse_detail(self, response):
        #     print response.url
