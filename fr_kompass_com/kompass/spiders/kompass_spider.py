import scrapy

from kompass.items import KompassItem
from kompass.pipelines import KompassPipeline


class KompassSpider(scrapy.Spider):
    counter = 0
    name = "kompass"
    allowed_domains = ["fr.kompass.com"]

    start_urls = (
        'http://fr.kompass.com/en/d/paris/fr_11_75/',
    )

    pipeline = set([
        KompassPipeline,
    ])


    def parse(self, response):
        div_info= response.xpath("//div[@class='facetValues']")[1]
        links = div_info.xpath("ul/li/a")

        for link in links:
            link_url = link.xpath("@href").extract()[0]
            link_name = link.xpath("text()").extract()[0].strip()
            url = response.urljoin(link_url)
            meta_info = {'category':link_name}
            yield scrapy.Request(url, meta=meta_info, callback=self.parse_category)

    def parse_category(self, response):
        category_name = response.meta['category']
        meta_info = {'category':category_name}
        prod_list = response.xpath("//div[@id='resultatDivId']/div[@class='prod_list']")
        for prod in prod_list:
            name = prod.xpath("div[contains(@class,'details')]/a/@href").extract()
            url_prod = response.urljoin(name[0])
            yield scrapy.Request(url_prod, meta=meta_info, callback=self.parse_page)

        next_link = response.xpath("//ul[@id='paginatorDivId']/li[@class='active']/following-sibling::li[1]/a/@href")

        if next_link:
            url = response.urljoin(next_link.extract()[0])
            yield scrapy.Request(url, meta=meta_info, callback=self.parse_category)


    def parse_page(self, response):
        item = KompassItem()
        name = response.xpath("//h1/text()").extract()
        address = response.xpath("//div[@class='infos']/div[@class='addressCoordinates']/p[1]/node()").extract()
        item['name'] = name
        item['category'] = response.meta['category']
        item['address'] = address
        yield item


