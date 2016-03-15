# -*- coding: utf-8 -*-

import re
import scrapy

from ohranagovby.items import OhranagovbyItem


class OhranagovbySpider(scrapy.Spider):
    name = "ohranagovby"
    allowed_domains = ["ohrana.gov.by"]
    start_urls = [
        "http://ohrana.gov.by/wp/about-department/territorial-authorities/",
    ]

    def __init__(self):
        self.counter_item = 0

    def parse(self, response):
        for entry in response.xpath('//div[@class="entry-content"]/p'):
            raw = entry.extract()
            raw_list = raw.split('<br>')
            name = entry.xpath("strong/a/text()").extract()
            if not name:
                name = entry.xpath("a/strong/text()").extract()
            item = OhranagovbyItem()
            item['name'] = name
            item['address'] = raw_list[1].strip()
            item['phone'] = [re.sub('\W', '', raw_list[2])]
            item['url'] = response.url
            item['phone_code'] = u""
            yield item
            href = entry.xpath("strong/a/@href").extract()
            if not href:
                href = entry.xpath("a/@href").extract()
            url = response.urljoin(href[0])

            request = scrapy.Request(url, callback=self.parse_page)
            yield request

    def parse_page(self, response):
        pattern = "//ul[@class='sub-menu']/li/a[re:test(text(),'%s')]/@href" % u'подразд|ПОДРАЗД|Подразд'
        curr_url = response.url
        region = curr_url[7:curr_url.find('.')]

        if region == "mou":
            pattern_otdel = "//ul[@class='sub-menu']/li/a[re:test(text(),'%s')]/@href" % u'ОТДЕЛ|отдел'
            links = response.xpath(pattern_otdel)

            for link in links:
                url = response.urljoin(link.extract())
                yield scrapy.Request(url, callback=self.parse_page_from_mou)
        else:
            href = response.xpath(pattern)
            if href:
                url = response.urljoin(href.extract()[0])
                yield scrapy.Request(url, callback=self.parse_page_struct, meta={'region': region, 'region_url':response.url})

    def parse_page_struct(self, response):
        region = response.meta['region']
        region_url = response.meta['region_url']

        if region == "brest":
            items = response.xpath("//div[@class='entry-content']/blockquote/p")
            for item in items:
                raw = item.extract()
                raw_list = raw.split('<br>')
                work_time = response.xpath("//div[@class='entry-content']/p[@class='style6'][2]/strong/text()").extract()
                otdel = OhranagovbyItem()
                otdel['name'] = raw_list[0]
                address = raw_list[1]
                otdel['address'] = address
                m = re.search('\(.+\)', address)
                if m:
                    code_phone = m.group(0)
                    code_phone = re.sub('\D', '', code_phone)

                otdel['phone_code'] = code_phone

                phones = []
                for p in raw_list[2:]:
                    if re.sub('\D', '', p):
                        p = re.sub(u'вел', ',8029',p)
                        p = re.sub(u'мтс', ',8033',p)
                        p = re.sub(u'[А-Я а-я.:]*', '', p)

                        mt = re.search('\-[\d]{3,4}\-', p)
                        if mt:
                            f_m = mt.group(0)
                            pos = p.find(f_m) + 3
                            p = p[:pos] + ',' + p[pos:]

                        phones.append(p)

                otdel['phone'] = phones
                otdel['url'] = region_url
                yield otdel
        elif region == "vitebsk":
            items_content = response.xpath("//div[@class='entry-content']")
            items = items_content.extract()[0].split(u'<p>\xa0</p>')
            for item in items:
                raw = item.split('</p>')
                name = u''
                address = u''
                status = False

                for r in raw:
                    pattern = u'\<[^>]*\>'
                    elem = re.sub(pattern, '', r)
                    if re.search(u'Глубокский', elem):
                        name2 = re.sub(pattern, '', raw[6])
                        address2 = re.sub(pattern, '', raw[7])
                        phones2 = [re.sub(pattern, '', raw[9])]
                        status = True
                        name = re.sub(pattern, '', raw[0])
                        address = re.sub(pattern, '', raw[1])
                        phones = [re.sub(pattern, '', raw[3])]
                        break

                    name = re.sub(pattern, '', raw[0])
                    address = re.sub(pattern, '', raw[1])
                    if re.search(u'\d{6}', address):
                        phones = raw[2:]
                    else:
                        address = re.sub(pattern, '', raw[2])
                        phones = raw[3:]

                otdel = OhranagovbyItem()
                otdel['name'] = name
                otdel['address'] = address
                otdel['phone'] = phones
                otdel['url'] = region_url
                otdel['phone_code'] = u""
                yield otdel

                if status:
                    otdel2 = OhranagovbyItem()
                    otdel2['name'] = name2
                    otdel2['address'] = address2
                    otdel2['phone'] = phones2
                    otdel2['url'] = region_url
                    yield otdel2

        elif region == "gomel":
            items = response.xpath("//div[@class='entry-content']/p")
            for item in items:
                raw = item.extract()
                raw_list = raw.split('<br>')
                addr_an_ph = raw_list[1]
                pos_ph = addr_an_ph.find(u'тел.')
                otdel = OhranagovbyItem()
                otdel['name'] = raw_list[0]
                otdel['address'] = addr_an_ph[:pos_ph]
                otdel['phone'] = [addr_an_ph[pos_ph:]]
                otdel['url'] = region_url
                otdel['phone_code'] = u""
                yield otdel
        elif region == "grodno":
            items = response.xpath("//div[@class='entry-content']/table/tbody/tr")
            for item in items:
                name = item.xpath("td[1]/strong[1]/text()").extract()
                address = item.xpath("td[1]/p[1]/text()").extract()
                phones = item.xpath("td[1]/p[2]/text()").extract()
                otdel = OhranagovbyItem()
                otdel['name'] = name
                otdel['address'] = address
                otdel['phone'] = phones
                otdel['url'] = region_url
                otdel['phone_code'] = u""
                yield otdel
                pat = u"td[1]/p[re:test(text(),'%s')]" % u'Отдел'
                name_add = item.xpath(pat)
                if len(name_add)>0:
                    otdel_add = OhranagovbyItem()
                    otdel_add['name'] = name_add.xpath("text()").extract()
                    #following-sibling::p[1]/text()
                    address_add = name_add.xpath("following-sibling::p[1]/text()").extract()
                    phones_add = name_add.xpath("following-sibling::p[2]/text()").extract()
                    if not address_add:
                        address_add = address

                    if len(phones_add) == 0 or phones_add[0] == u'\xa0':
                        phones_add = phones

                    otdel_add['address'] = address_add
                    otdel_add['phone'] = phones_add
                    otdel_add['url'] = region_url
                    otdel_add['phone_code'] = u""
                    yield otdel_add




        elif region == "minsk":
            links = response.xpath("//div[@class='entry-content']/ul/li/strong/a/@href")
            for link in links:
                url = response.urljoin(link.extract())
                yield scrapy.Request(url, callback=self.parse_minsk)
        elif region == "mogilev":
            links = response.xpath("//div[@class='entry-content']/table[@class='category']/tbody/tr/td/span/a/@href")
            for link in links:
                url = response.urljoin(link.extract())
                yield scrapy.Request(url, callback=self.parse_mogilev)
        else:
            pass

    def parse_page_from_mou(self, response):
        item = OhranagovbyItem()
        item['name'] = response.xpath("//header/h1/text()").extract()[0]
        item['address'] = response.xpath("//div[@class='entry-content']/div[1]").extract()
        item['phone'] = response.xpath("//div[@class='entry-content']/p[1]").extract()
        item['url'] = u"http://mou.ohrana.gov.by/"
        item['phone_code'] = u""
        yield item

    def parse_mogilev(self, response):
        info = response.xpath("//div[@class='entry-content']/p")
        pat = u'\<[^>]*\>'
        if info:
            item = OhranagovbyItem()
            name = re.sub(pat, '', info[0].extract())
            if re.search(u'г\.\s*Белыничи', name):
                item['name'] = u"Белыничское отделение "
                item['address'] = re.sub(pat, '', info[0].extract())
                item['phone'] = [re.sub(pat, '', info[1].extract())]
                item['phone_code'] = u""
                # item['phone'] = info[1].extract()
            else:
                item['name'] = re.sub(pat, '', info[0].extract())
                item['address'] = re.sub(pat, '', info[1].extract())
                item['phone'] = [re.sub(pat, '', info[2].extract())]
                item['phone_code'] = u""
            item['url'] = u"http://mogilev.ohrana.gov.by/"
            yield item

    def parse_minsk(self, response):
        pattern = "//div[@class='entry-content']/div/div/div[@class='otdely_text']/div"
        ptn_ph = "//div[@class='entry-content']/div/div/div[@class='otdely_text']/div/p[re:test(text(),'%s')]/text()"\
                        % u'тел|Тел'

        for d in response.xpath(pattern):
            h4 = d.xpath("h4/text()").extract()
            if re.search(u'Наш', h4[0]):
                address = d.xpath("p/text()").extract()

        item = OhranagovbyItem()
        item['name'] = response.xpath("//header/h1/text()").extract()[0]
        item['address'] = address
        item['phone'] = response.xpath(ptn_ph).extract()
        item['url'] = u"http://minsk.ohrana.gov.by/"
        item['phone_code'] = u""
        yield item
