import scrapy

from eda.items import EdaItem


class EdaSpder(scrapy.Spider):
    name = 'eda'
    allowed_domains = ["eda.ru"]
    start_urls = (
        'http://eda.ru/',
    )

    categories_ids = []

    def parse(self, response):
        categories = response.xpath("//div[@class='b-list-categories']/ul/li/a")
        kol = 0
        for cat in categories:
            name = cat.xpath("@data-tag-name").extract()
            cat_url = cat.xpath("@href").extract()
            if cat_url:
                kol += 1
                cat_url = response.urljoin(cat_url[0])

                yield scrapy.Request(cat_url, callback=self.parse_category)

    def parse_category(self, response):
        h1_title = response.xpath("//h1/a/text()")
        h1_title_id = response.xpath("//h1/a/@id").extract()[0]

        recipies = response.xpath("//div[contains(@class,'b-list-items')]/div[contains(@class,'b-recipe-widget')]")
        first_nav_info = response.xpath("//a[@class='subnav__link-mainpage subnav__link-aside']")

        first_nav = []
        for fn in first_nav_info:
            fn_url = fn.xpath("@href").extract()
            fn_name = fn.xpath("text()").extract()
            first_nav.append({'name': fn_name[0], 'url': fn_url[0]})

        for recipe in recipies:
            r_link = recipe.xpath("div/div/div/h3/a/@href").extract()
            r_name = recipe.xpath("div/div/div/h3/a/text()").extract()
            meta_info = {
                'category_name': h1_title_id,
                'first_nav': first_nav,
                'category_url': response.url
            }
            r_link = r_link[0]
            yield scrapy.Request(r_link, meta=meta_info, callback=self.parse_recipe)

    def parse_recipe(self, response):
        name = response.xpath("//h1/text()")
        recipe_date = response.xpath("//div[@class='recipe-published']/span[@class='date']/text()")
        time_cook = response.xpath("//time[@class='value-title']/text()")
        author_info = response.xpath("//a[@id='link-recipeAuthor-name']/span/text()")
        ingredients = response.xpath("//table/tbody/tr[@class='ingredient']")
        description = response.xpath("//p[@itemprop='description']/text()")
        image_info = response.xpath("//div[@id='s-photoListContainer']/img/@src")
        if image_info:
            img = image_info.extract()[0]
        else:
            img = ''

        item = EdaItem()
        item['category_name'] = response.meta['category_name']
        item['category_url'] = response.meta['category_url']
        item['first_nav'] = response.meta['first_nav']
        item['recipe_name'] = name.extract()[0]
        item['recipe_cooking_time'] = time_cook.extract()
        item['recipe_author'] = author_info.extract()
        item['recipe_url'] = response.url
        item['description'] = description.extract()
        item['date'] = recipe_date.extract()
        item['image'] = img

        ingredients_list = []

        for ingr in ingredients:
            ingredients_list.append({"name": ''.join(ingr.xpath("td[1]/a/text()").extract()),
                                     "quantity": ''.join(ingr.xpath("td[2]/span/text()").extract())
                                     })

        item['ingredients'] = ingredients_list
        yield item


        # print time_cook.extract()[0]
        # print name.extract()[0]
        # print recipe_date.extract()[0]
        # print response.url