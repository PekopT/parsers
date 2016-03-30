# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.http import FormRequest

from iafd.items import IafdActorsItem, IafdDistributorItem, IafdStudioItem, IafdTitleItem
from iafd.pipelines import IafdActorsPipeline, IafdStudioPipeline, IafdDistributorPipeline, IafdTitlePipeline


class ActorsSpider(scrapy.Spider):
    counter = 0
    name = "iafd_actors"
    allowed_domains = ["iafd.com"]
    start_urls = (
        'http://www.iafd.com/astrology.asp',
    )

    pipeline = set([
        IafdActorsPipeline,
    ])

    def parse(self, response):
        links = response.xpath("//div[@class='col-lg-2 col-sm-4 col-xs-6 text-center']/a/@href").extract()
        for href in links:
            self.counter += 1
            url = response.urljoin(href)
            yield scrapy.Request(url, callback=self.parse_page)

    def parse_page(self, response):
        it = 0
        for link in response.xpath("//div[@id='astro']/div[@class='perficon']/a/@href").extract():
            it += 1
            url = response.urljoin(link)

            yield scrapy.Request(url, callback=self.parse_page_detail)

    def parse_page_detail(self, response):
        title = response.xpath("//div[@class='container']/div[@class='row']/div/h1/text()").extract()
        # vitalbox = response.xpath("//div[@class='container']/div[@class='row']/div/div[@id='perfbox']/div[@id='vitalbox']/div[@id='home']")
        # ethnicity_patt = "//div[@class='container']/div[@class='row']/div/div[@id='perfbox']/div[@id='vitalbox']/div[@id='home']/div/div[1]/p[@class='biodata'][1]/text()"
        # nationality = vitalbox.xpath("div/div[1]/p[@class='biodata'][2]/text()").extract()
        # haircolors = vitalbox.xpath("div/div[1]/p[@class='biodata'][3]/text()").extract()
        # height = vitalbox.xpath("div/div[2]/p[@class='biodata'][1]/text()").extract()
        # weight = vitalbox.xpath("div/div[2]/p[@class='biodata'][2]/text()").extract()
        info = response.xpath("//div[@class='container']/div[@class='row'][2]/div")
        home_info = response.xpath("//div[@id='home']/div")
        ethnicity = home_info.xpath(
            "div/p[@class='bioheading' and re:test(text(), 'Ethnicity')]/following-sibling::p[1]/text()").extract()
        nationality = home_info.xpath(
            "div/p[@class='bioheading' and re:test(text(), 'Nationality')]/following-sibling::p[1]/text()").extract()
        haircolors = home_info.xpath(
            "div/p[@class='bioheading' and re:test(text(), 'Hair Colors')]/following-sibling::p[1]/text()").extract()
        height = home_info.xpath(
            "div/p[@class='bioheading' and re:test(text(), 'Height')]/following-sibling::p[1]/text()").extract()
        weight = home_info.xpath(
            "div/p[@class='bioheading' and re:test(text(), 'Weight')]/following-sibling::p[1]/text()").extract()

        image = info.xpath("div[@id='headshot']/img/@src").extract()
        performer_aka = info.xpath(
            "p[@class='bioheading' and re:test(text(), 'Performer')]/following-sibling::div[1]/text()").extract()
        init_place = info.xpath(
            "p[@class='bioheading' and re:test(text(), 'Birthplace')]/following-sibling::p[1]/text()").extract()
        init_date = info.xpath(
            "p[@class='bioheading' and re:test(text(), 'Birthday')]/following-sibling::p[1]/a/text()").extract()

        end_date = info.xpath(
            "p[@class='bioheading' and re:test(text(), 'Death')]/following-sibling::p[1]/a/text()").extract()

        years = info.xpath(
            "p[@class='bioheading' and re:test(text(), 'Years')]/following-sibling::p[1]/text()").extract()

        # ethnicity = response.xpath(patt)

        projects = []
        project_info = response.xpath("//table[@id='personal']/tbody/tr")

        for p in project_info:
            proj_url = p.xpath("td[1]/a/@href").extract()
            if proj_url:
                proj_url = proj_url[0]
            project_url = response.urljoin(proj_url)
            project_url = project_url.rstrip("/")
            url_data = project_url.split("/")
            project = {}

            project[u"Role"] = u"Actor@on",
            project[u"value"] = u"[[#ext_iafd_film_{0}]]".format(url_data[-1:][0][0:-4])
            project[u"url"] = project_url

            projects.append(project)

        item = IafdActorsItem()
        item['name'] = title
        item['url'] = response.url
        item['init_place'] = init_place
        item['init_date'] = init_date
        item['end_date'] = end_date
        item['performer'] = performer_aka
        item['projects'] = projects
        item['years'] = years
        item['image'] = image
        item['hair_colors'] = haircolors
        item['weight'] = weight
        item['height'] = height
        item['ethnicity'] = ethnicity
        item['nationality'] = nationality

        yield item


class TitlesSpider(scrapy.Spider):
    counter = 0
    name = 'iafd_titles'
    allowed_domains = ["iafd.com"]
    start_urls = (
        'http://www.iafd.com/studio.asp',
    )

    pipeline = set([
        IafdTitlePipeline,
    ])

    def parse(self, response):
        for option in response.xpath("//select[@name='Studio']/option/@value").extract():
            self.counter += 1
            if self.counter < 5:
                yield FormRequest("http://www.iafd.com/studio.rme",
                              formdata={u'Studio': option},
                              callback=self.parse_page)

    def parse_page(self, response):
        for item in response.xpath("//table[@id='studio']/tbody/tr/td[1]"):
            href = item.xpath('a/@href').extract()[0]
            url = response.urljoin(href)
            yield scrapy.Request(url, callback=self.parse_title_page)

    def get_url_data(self, url):
        udm = re.search(u"gender.+", url)
        if udm:
            url_data_search = udm.group(0)
        url_data = url_data_search.split('/')
        return url_data

    def get_male(self, value):
        url_data = self.get_url_data(value)
        male = url_data[0][-1:]
        return male

    def get_name_htm(self, value):
        url_data = self.get_url_data(value)
        return url_data[1]

    def parse_title_page(self, response):
        info = response.xpath("//div[@class='container']/div[@class='row'][2]/div")
        title = response.xpath("//h1/text()").extract()
        release = info.xpath(
            "p[@class='bioheading' and re:test(text(), 'Release Date')]/following-sibling::p[1]/text()")
        duration = info.xpath("p[@class='bioheading' and re:test(text(), 'Minutes')]/following-sibling::p[1]/text()")

        performers = response.xpath(
            "//div[@class='container']/div[@class='row'][2]/div[2]/div/div[@class='padded-panel']/div/div/div[@class='castbox']")

        actors = []
        for p in performers:
            actor_url = p.xpath("p/a/@href").extract()
            if actor_url:
                actor_url = actor_url[0]
            actor_url = response.urljoin(actor_url)
            actor_value = u"[[#ext_iafd_{0}_{1}]]".format(self.get_male(actor_url), self.get_name_htm(actor_url))
            actor = {}
            actor[u"Role"] = u"Actor@on"
            actor[u"value"] = actor_value
            actor[u"url"] = actor_url
            actors.append(actor)

        director_info = info.xpath("p[@class='bioheading' and re:test(text(), 'Director')]/following-sibling::p[1]/a")

        director = {}
        if len(director_info) > 0:
            director_url = director_info.xpath('@href').extract()[0]
            director_url = response.urljoin(director_url)
            director_value = u"[[#ext_iafd_{0}_{1}]]".format(self.get_male(director_url),
                                                             self.get_name_htm(director_url))

            director[u"Role"] = u"Director@on"
            director[u"value"] = director_value
            director[u"url"] = director_url

        distrib_info = info.xpath("p[@class='bioheading' and re:test(text(), 'Distributor')]/following-sibling::p[1]")
        distrib_url = distrib_info.xpath('a/@href').extract()

        distributor = {}
        if distrib_url:
            distrib_url = distrib_url[0]
            distrib_url = response.urljoin(distrib_url)
            distrub_url_data = distrib_url.rstrip('/').split('/')
            dist_sub = distrub_url_data[-1:][0][0:-4]
            dist_val = u"[[#ext_iafd_distrib_{0}]]".format(dist_sub)

            distributor[u"Role"] = u"Distributor@on"
            distributor[u"value"] = dist_val
            distributor[u"url"] = distrib_url

        studio = {}
        studio_info = info.xpath("p[@class='bioheading' and re:test(text(), 'Studio')]/following-sibling::p[1]")
        studio_url = studio_info.xpath('a/@href').extract()
        if studio_url:
            studio_url = studio_url[0]
            studio_url = response.urljoin(studio_url)
            studio_url_data = studio_url.rstrip('/').split('/')
            studio_sub = studio_url_data[-1:][0][0:-4]
            stud_val = u"[[#ext_iafd_studio_{0}]]".format(studio_sub)

            studio[u"Role"] = u"Studio@on"
            studio[u"value"] = stud_val
            studio[u"url"] = studio_url

        item = IafdTitleItem()
        item['name'] = title
        item['url'] = response.url
        item['release_date'] = release.extract()
        item['duration'] = duration.extract()
        item['studio'] = studio
        item['distributor'] = distributor
        item['director'] = director
        item['actors'] = actors

        yield item


class DistributorsSpider(scrapy.Spider):
    counter = 0
    name = 'iafd_distributors'
    allowed_domains = ["iafd.com"]
    start_urls = (
        'http://www.iafd.com/distrib.asp',
    )

    pipeline = set([
        IafdDistributorPipeline,
    ])

    def parse(self, response):
        for option in response.xpath("//select[@name='Distrib']/option/@value").extract():
            self.counter += 1
            yield FormRequest("http://www.iafd.com/distrib.rme",
                              formdata={u'Distrib': option},
                              callback=self.parse_page)

    def parse_page(self, response):
        title = response.xpath("//h2/text()").extract()[0]
        related = []
        for r in response.xpath("//table[@id='distable']/tbody/tr/td[1]"):
            href = u"#ext_iafd_" + r.xpath('a/@href').extract()[0]
            value = r.xpath('a/text()').extract()
            related.append({'value': value, 'url': href})
        item = IafdDistributorItem()
        item['name'] = title
        item['url'] = response.url
        item['related'] = related
        yield item


class StudiosSpider(scrapy.Spider):
    counter = 0
    name = 'iafd_studios'
    allowed_domains = ["iafd.com"]
    start_urls = (
        'http://www.iafd.com/studio.rme',
    )

    pipeline = set([
        IafdStudioPipeline,
    ])

    def parse(self, response):
        for option in response.xpath("//select[@name='Studio']/option/@value").extract():
            self.counter += 1
            yield FormRequest("http://www.iafd.com/studio.rme",
                              formdata={u'Studio': option},
                              callback=self.parse_page)

    def parse_page(self, response):
        title = response.xpath("//h2/text()").extract()[0]
        related = []
        for r in response.xpath("//table[@id='studio']/tbody/tr/td[1]"):
            href = u"#ext_iafd_" + r.xpath('a/@href').extract()[0]
            value = r.xpath('a/text()').extract()
            related.append({'value': value, 'url': href})

        item = IafdStudioItem()
        item['name'] = title
        item['url'] = response.url
        item['related'] = related
        yield item
