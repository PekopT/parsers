# -*- coding: utf-8 -*-
import scrapy
from menu.items import MenuItem


class MenuSpder(scrapy.Spider):
    name = 'menu'
    allowed_domains = ["1000.menu"]
    start_urls = (
        'http://1000.menu/',
    )

    categories_ids = []

    def parse(self, response):
        categories = response.xpath("//div[@class='catalog_tree']/div[@class='item'][2]/ul/li")

        first_nav_main = []
        for cat in categories:
            fn_name = cat.xpath("a/text()").extract()
            fn_url = cat.xpath("a/@href").extract()[0]
            fn_url = response.urljoin(fn_url)
            first_nav_main.append({'name': fn_name[0], 'url': fn_url})

        recipies = response.xpath(
            "//div[@class='rating-block'][3]/div[@class='cooking-block']/div[@class='item cooking']")
        for recipe in recipies:
            r_link = recipe.xpath("div[@class='name elli multiline']/a/@href").extract()
            meta_info = {
                'category_name': u"Главная страница",
                'first_nav': first_nav_main,
                'category_url': response.url,
            }
            r_link = response.urljoin(r_link[0])
            yield scrapy.Request(r_link, meta=meta_info, callback=self.parse_recipe)

        kol = 0
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
        category_name = response.xpath("//h1[@itemprop='name']/text()").extract()
        category_name = ''.join(category_name)
        categories = response.xpath("//div[@class='main-top']/nav/ul/li/a")
        first_nav = []
        for scat in categories:
            fn_name = scat.xpath("text()").extract()
            fn_url = scat.xpath("@href").extract()[0]
            fn_url = response.urljoin(fn_url)
            first_nav.append({'name': fn_name[0], 'url': fn_url})

        recipies = response.xpath("//div[@class='cooking-block']/div[@class='anonce-cont-side']")
        for recipe in recipies:
            r_link = recipe.xpath("a/@href").extract()
            meta_info = {
                'category_name': category_name,
                'first_nav': first_nav,
                'category_url': response.url,
            }
            r_link = response.urljoin(r_link[0])
            yield scrapy.Request(r_link, meta=meta_info, callback=self.parse_recipe)

        for scat in categories:
            cat_url = scat.xpath("@href").extract()
            cat_url = response.urljoin(cat_url[0])
            meta_info = {'category_name': ''}
            yield scrapy.Request(cat_url, meta=meta_info, callback=self.parse_category)

    def parse_recipe(self, response):
        name = response.xpath("//h1[@itemprop='name']/text()").extract()
        description = response.xpath("//p[@class='shorten']/node()").extract()
        author_info_parent = response.xpath("//div[contains(@class,'recipe-top-1')]")
        image_info = response.xpath("//div[@class='main-photo']/a/img/@src").extract()

        if author_info_parent:
            author_pattern = "p/span[re:test(text(),'%s')]/following-sibling::a/text()" % u"Автор"
            author_info = author_info_parent.xpath(author_pattern)
            author = ','.join([auth for auth in author_info.extract()])
            time_cook = author_info_parent.xpath("p/span[@class='cooktime']/text()").extract()

        ingredients_list = []
        ingredients = response.xpath("//div[@id='recept-list']/div[@class='recept-list-left clf']")
        for ingr in ingredients:
            ingr_name = ingr.xpath("p[1]/a/text()").extract()
            ingr_quantity = ingr.xpath("p[2]/span[@class='squant']/text()").extract()
            ingr_recalc_s_num = ingr.xpath("p[2]/select[@class='recalc_s_num']/option[@selected]/text()").extract()

            ingredients_list.append({"name": ''.join(ingr_name).strip(),
                                     "quantity": ''.join(ingr_quantity).strip() + ' ' +''.join(ingr_recalc_s_num).strip()
                                     })


        item = MenuItem()
        item['category_name'] = response.meta['category_name']
        item['category_url'] = response.meta['category_url']
        item['first_nav'] = response.meta['first_nav']

        item['recipe_name'] = name[0]
        item['recipe_cooking_time'] = time_cook
        item['recipe_author'] = author
        item['recipe_url'] = response.url
        item['description'] = description
            # item['date'] = recipe_date
        item['image'] = image_info
        item['ingredients'] = ingredients_list

        yield item
