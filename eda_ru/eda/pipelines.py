# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from codecs import getwriter
from sys import stdout
import json
import re

sout = getwriter("utf8")(stdout)


class EdaPipeline(object):
    category_recipes = {}

    def process_item(self, item, spider):
        category_name = item['category_name']
        # print category_name


        if category_name not in self.category_recipes:
            self.category_recipes[category_name] = {}
            self.category_recipes[category_name]['recipes'] = []

        recipe_row = {}
        if item['recipe_name']:
            recipe_row['name'] = item['recipe_name']
        recipe_row['cooking_time'] = item['recipe_cooking_time']
        recipe_row['author'] = item['recipe_author']
        recipe_row['desc'] = item['description']
        recipe_row['url'] = item['recipe_url']
        recipe_row['date'] =  item['date']
        recipe_row['ingredients'] =  item['ingredients']
        if item['image']:
            recipe_row['image'] =  ''.join(item['image'])


        self.category_recipes[category_name]['recipes'].append(recipe_row)
        self.category_recipes[category_name]['name'] = category_name
        self.category_recipes[category_name]['url'] = item['category_url']
        self.category_recipes[category_name]['first_nav_block'] = item['first_nav']

    def close_spider(self, spider):
        # print self.category_recipes
        for key in self.category_recipes:
            sout.write(json.dumps(self.category_recipes[key], ensure_ascii=False) + "\n")
