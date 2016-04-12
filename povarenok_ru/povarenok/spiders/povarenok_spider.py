# -*- coding: utf-8 -*-
import scrapy

from povarenok.items import PovarenokItem


class PovarenokSpder(scrapy.Spider):
    name = 'povarenok'
    allowed_domains = ["www.povarenok.ru"]
    start_urls = (
        'http://www.povarenok.ru/',
    )

    categories_ids = []

    def parse(self, response):
        category_name = response.xpath("//h1[@class='h1title']/a/text()").extract()[0]

        first_nav = []
        categories = response.xpath("//ul[@id='recipes_category']/li")
        for cat in categories:
            fn_name = cat.xpath("a/text()").extract()
            fn_url = cat.xpath("a/@href").extract()
            first_nav.append({'name': fn_name[0], 'url': fn_url[0]})


        recipies = response.xpath("//div[@class='mainrecipes']/table")
        for recipe in recipies:
            r_link = recipe.xpath("tbody/tr/td[1]/h1/a/@href").extract()
            meta_info = {
                'category_name': category_name,
                'first_nav': first_nav,
                'category_url': response.url,
            }
            r_link = response.urljoin(r_link[0])
            yield scrapy.Request(r_link, meta=meta_info, callback=self.parse_recipe)

        kol = 0

        for cat in categories:
            kol +=1
            cat_name = cat.xpath("a/text()").extract()
            cat_url = cat.xpath("a/@href").extract()
            if cat_url:
                cat_url = response.urljoin(cat_url[0])
                    yield scrapy.Request(cat_url, callback=self.parse_category)

    def parse_category(self, response):
        current_url = response.url.replace('http://www.povarenok.ru','')[:-1]
        main_title = response.xpath("//h1/text()").extract()
        pattern = "//li/a[@href='%s']/parent::li/ul/li" % current_url
        categories = response.xpath(pattern)

        if main_title:
            main_title = main_title[0]

        first_nav  = []
        for cat in categories:
            fn_name = cat.xpath("a/text()").extract()
            fn_url = cat.xpath("a/@href").extract()
            first_nav.append({'name': fn_name[0], 'url': fn_url[0]})

        recipies = response.xpath("//table[@class='uno_recipie']")
        for recipe in recipies:
            r_name = recipe.xpath("tbody/tr/td[1]/h1/a/text()").extract()
            r_link = recipe.xpath("tbody/tr/td[1]/h1/a/@href").extract()
            meta_info = {
                'category_name': main_title,
                'first_nav': first_nav,
                'category_url': response.url,
            }
            if r_link:
                r_link = response.urljoin(r_link[0])
                yield scrapy.Request(r_link, meta=meta_info, callback=self.parse_recipe)

        for cat in categories:
            cat_name = cat.xpath("a/text()").extract()
            cat_url = cat.xpath("a/@href").extract()
            if cat_url:
                cat_url = response.urljoin(cat_url[0])
                yield scrapy.Request(cat_url, callback=self.parse_category)


    def parse_recipe(self, response):
        name = response.xpath("//div[@id='print_body']/h1/a/text()").extract()
        if not name:
            name = response.xpath("//div[@id='print_body']/h1/text()").extract()

        image = response.xpath("//div[@class='recipe-img']/img/@src").extract()

        description = response.xpath("//div[@class='recipe-short']/span[@itemprop='summary']/text()").extract()
        author = response.xpath("//span[@itemprop='author']/text()").extract()
        recipe_date = response.xpath("//span[@class='recipe-date']/text()").extract()
        ingredients = response.xpath("//span[@itemprop='ingredient']")

        ingredients_list = []
        for ingr in ingredients:
            ingr_name = ingr.xpath("a/span/text()").extract()
            quantity = ingr.xpath("span[@itemprop='amount']/text()").extract()
            if quantity:
                quantity = quantity[0].strip()
            else:
                quantity = ingr.xpath("text()").extract()[0].strip()


            if not ingr_name:
                ingr_name = ingr.xpath("span[@itemprop='name']/text()").extract()
            ingredients_list.append({"name": ingr_name[0].strip(),
                                     "quantity":quantity
            })


        item = PovarenokItem()
        item['category_name'] = response.meta['category_name']
        item['category_url'] = response.meta['category_url']
        item['first_nav'] = response.meta['first_nav']
        item['recipe_name'] = name[0]
        item['recipe_author'] = author
        item['recipe_url'] = response.url
        item['description'] = description
        item['date'] = recipe_date
        item['image'] = image
        item['ingredients'] = ingredients_list

        yield item


