# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
import scrapy


class EdaItem(scrapy.Item):
    category_name = scrapy.Field()
    category_url = scrapy.Field()
    name = scrapy.Field()
    recipies = scrapy.Field()
    recipe_name = scrapy.Field()
    first_nav = scrapy.Field()
    recipe_cooking_time = scrapy.Field()
    recipe_author = scrapy.Field()
    recipe_url = scrapy.Field()
    description = scrapy.Field()
    date = scrapy.Field()
    ingredients = scrapy.Field()
    image = scrapy.Field()
    type = scrapy.Field()
    recipe_video = scrapy.Field()
