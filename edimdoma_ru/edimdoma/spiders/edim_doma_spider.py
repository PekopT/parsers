# -*- coding: utf-8 -*-
import scrapy

from edimdoma.items import EdimdomaItem

class EdimdomaSpder(scrapy.Spider):
    name = 'edimdoma'
    allowed_domains = ["www.edimdoma.ru"]
    start_urls = (
        'http://www.edimdoma.ru/retsepty',
    )

    categories_ids = []

    def parse(self, response):
        categories = response.xpath("//div[@class='b-page_block m-type-1 left_menu']/div/div/ul/li")
        kol = 0
        main_title = response.xpath("//h1/text()").extract()[0]

        first_nav_main = []
        for cat in categories:
            fn_name = cat.xpath("a/text()").extract()
            fn_url = cat.xpath("a/@href").extract()
            first_nav_main.append({'name': fn_name[0], 'url': fn_url[0]})

        recipies = response.xpath("//div[@class='b-belt__clause g-cleared']")
        for recipe in recipies:
            r_link = recipe.xpath("div/div/div/h2/a/@href").extract()
            # r_name = recipe.xpath("div/div/div/h2/a/text()").extract()
            rating_info = recipe.xpath("div/div/div/div/div/div/ul/li[@class='show-value']/text()")
            rating_text = rating_info.extract()[0]
            rating_data = rating_text.split(':')
            rating = rating_data[1].split(u'из')[0].strip()
            meta_info = {
                'category_name': main_title,
                'first_nav': first_nav_main,
                'rating': rating,
                'category_url': response.url,
            }
            r_link = r_link[0]
            yield scrapy.Request(r_link, meta=meta_info, callback=self.parse_recipe)


        for cat in categories:
            cat_name = cat.xpath("a/text()").extract()
            cat_url = cat.xpath("a/@href").extract()
            if cat_url:
                kol += 1
                cat_url = response.urljoin(cat_url[0])
                if cat_name:
                    cat_name = cat_name[0]
                else:
                    cat_name = ''
                meta_info = {'category_name': cat_name}
                yield scrapy.Request(cat_url, meta=meta_info, callback=self.parse_category)


    def parse_category(self, response):
        sm_pat = "//div[@class='b-page_block m-type-1 left_menu']/div/div/ul/li/ul[@class='submenu__list__clause']/li"
        category_name = response.meta['category_name']

        first_nav = []
        submenu = response.xpath(sm_pat)
        for scat in submenu:
            fn_name = scat.xpath("a/text()").extract()
            fn_url = scat.xpath("a/@href").extract()
            first_nav.append({'name': fn_name[0], 'url': fn_url[0]})

        recipies = response.xpath("//div[@class='b-belt__clause g-cleared']")
        for recipe in recipies:
            r_link = recipe.xpath("div/div/div/h2/a/@href").extract()
            # r_name = recipe.xpath("div/div/div/h2/a/text()").extract()
            rating_info = recipe.xpath("div/div/div/div/div/div/ul/li[@class='show-value']/text()")
            rating_text = rating_info.extract()[0]
            rating_data = rating_text.split(':')
            rating = rating_data[1].split(u'из')[0].strip()
            meta_info = {
                'category_name': category_name,
                'first_nav': first_nav,
                'rating': rating,
                'category_url': response.url,
            }
            r_link = r_link[0]
            yield scrapy.Request(r_link, meta=meta_info, callback=self.parse_recipe)

        for cat in submenu:
            cat_name = cat.xpath("a/text()").extract()
            cat_url = cat.xpath("a/@href").extract()
            if cat_url:
                cat_url = response.urljoin(cat_url[0])
                if cat_name:
                    cat_name = cat_name[0]
                else:
                    cat_name = ''
                meta_info = {'category_name': cat_name}
                yield scrapy.Request(cat_url, meta=meta_info, callback=self.parse_category)


    def parse_recipe(self, response):
        name = response.xpath("//h1[@itemprop='name']/text()").extract()
        image = response.xpath("//div[@class='rec-picture']/a/img/@src").extract()
        time_cook = response.xpath("//strong[@itemprop='totalTime']/text()").extract()
        recipe_date = response.xpath("//div[@class='rec-info2']/div[@class='rec-added'][1]/text()").extract()
        description = response.xpath("//div[@itemprop='description']/node()").extract()
        author = response.xpath("//div[@class='rec-row']/span[contains(@class,'b-userinfo__clause')]/a/text()").extract()
        ingredients = response.xpath("//table[@class='rec-ingred-table']/tr")

        ingredients_list = []
        for ingr in ingredients:
            ingredients_list.append({"name": ''.join(ingr.xpath("td[1]/label/text()").extract()).strip(),
                                     "quantity": ''.join(ingr.xpath("td[2]/text()").extract()).strip()
                                     })

        item = EdimdomaItem()
        item['category_name'] = response.meta['category_name']
        item['category_url'] = response.meta['category_url']
        item['first_nav'] = response.meta['first_nav']
        item['rating'] = response.meta['rating']
        item['recipe_name'] = name[0]
        item['recipe_cooking_time'] = time_cook
        item['recipe_author'] = author
        item['recipe_url'] = response.url
        item['description'] = description
        item['date'] = recipe_date
        item['image'] = image
        item['ingredients'] = ingredients_list

        yield item


