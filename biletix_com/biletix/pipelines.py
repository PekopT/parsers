# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from codecs import getwriter
from sys import stdout
import json
import re

from utils import check_spider_close, check_spider_pipeline

CATEGORIES = {
    'FAMILY': 'family',
    'MUSIC':'muzik',
    'SPORT': 'sport',
    'ART': 'art',
    'OTHER': 'other'
}
sout = getwriter("utf8")(stdout)

class JsonPipeline(object):
    def __init__(self):
        self.data = []

    def validate_str(self, value):
        if type(value) == list:
            val = None
            for v in value:
                if v.strip():
                    val = v.strip()
                    break
            if val is None:
                return u''
        else:
            val = value
        return val.strip()

    def delete_tags(self, value):
        pattern = u'\<[^>]*\>'
        value = re.sub(pattern, '', value)
        value = re.sub(u'&#13;|&lt;|&gt;|<|>|\/li|\r\n', '', value)
        value = re.sub(u'td|span|\/|br', '', value)
        return value





class EventGroupPipeline(JsonPipeline):
    @check_spider_pipeline
    def process_item(self, item, spider):
        title = ''.join(item['title']).strip()
        init_date = ''.join(item['init_date'])
        end_date = ''.join(item['end_date'])
        place = ''.join(item['place'])
        description = ''.join(item['description'])
        images_list = [img for img in item['images']]

        row = {}
        ontoid = u"ext_biletix_etkinlik-grup_{0}_{1}".format(CATEGORIES[item['category']], item['id'])
        row["ontoid"] = ontoid

        row["Title"] = [{
            "value": title,
            "langua": "tr"
        }]

        if init_date:
            row["InitDate"] = [{"value": init_date.strip().split("T")[0]}]

        if end_date:
            row["EndDate"] = [{"value": end_date.strip().split("T")[0]}]

        images = []
        for img in images_list:
            image = {
                "src": [{"url": item['url']}],
                "value": img,
                "url": img
            }
            images.append(image)

        if images:
            row["Image"] = images

        row["isa"] = {}
        description = self.delete_tags(description).strip()
        if description:
            row["isa"]["Defin"] = [{
                "value": description,
                "langua": "tr"
            }]

        if u"MUSIC" in item['category'] or u"SPORT" in item['category']:
            subvalue = u"СultureEvent@on"
            if u"SPORT" in item['category']:
                subvalue = u"SportEvent@on"

            row["isa"]["otype"] = [{
                "value": "Event",
                "subvalue": subvalue
            }]
        else:
            row["isa"]["otype"] = "Event"

        row["Place"] = [{
            "value": place,
            "langua": "tr"
        }]

        participants = []

        for part in item['participants']:
            part_text = u"[[#ext_biletix_etkinlik_{0}_{1}]]".format(CATEGORIES[item['category']], part.split('/')[2])
            participants.append({"value":part_text})

        if participants:
            row["Participants"] = participants

        sout.write(json.dumps(row, ensure_ascii=False) + "\n")


class MekanPipeline(JsonPipeline):
    @check_spider_pipeline
    def process_item(self, item, spider):
        title = ''.join(item['title'])
        description = ''.join(item['description'])
        description = self.delete_tags(description).strip()
        images_list = [img for img in item['images']]
        projects_list = [pr for pr in item['projects']]
        place = ''.join(item['place']).strip()
        url = item['url']
        row = {}

        ontoid_data  = url.replace("http://","").split("/")
        ontoid = u"ext_biletix_mekan_{0}".format(ontoid_data[2])
        row["ontoid"] = ontoid

        row["ids"] = [{
            "type": "url",
            "value": url,
            "langua": "tr"
        }]

        row["Title"] = [{
            "value": title.strip(),
            "langua": "tr"
        }]
        images = []
        for img in images_list:
            image = {
                "src": [{"url": url}],
                "value": img,
                "url": img
            }
            images.append(image)

        if images:
            row["Image"] = images

        row["isa"] = {}

        if description:
            row["isa"]["Defin"] = [{
                "value": description,
                "langua": "tr"
            }]

        row["isa"]["otype"] = [{
                "value": u"Geo",
                "subvalue": u"Building@on"
        }]

        row["Countries"] = [{
            "value": u"Турция",
            "langua": u"ru"
        }]
        if place:
            row["Place"] = [{
            "value": place,
            "langua": "tr"
            }]
        projects = []
        for pr in projects_list:
            pr_data = pr.split('/')
            pr_text = u"[[#ext_biletix_etkinlik_müzik_{0}]]".format(pr_data[2])
            proj = {"value": pr_text}
            projects.append(proj)
        if projects:
            row["Projects"] = projects

        sout.write(json.dumps(row, ensure_ascii=False) + "\n")


class PersonaPipeline(JsonPipeline):
    def make_socials_row(self, social):
        social_row = []
        for soc in social:
            if u"Site" in soc['title']:
                id = {
                    "type": "official",
                    "value": soc['url'].strip(),

                }
            else:
                if u"twitter" in soc['title'].lower():
                    network = u"[[#ruw1108614|Twitter]]"
                elif u"facebook" in soc['title'].lower():
                    network = u"[[#ruw919912|Facebook]]"
                else:
                    network = u"[[]]"

                id = {
                    "type": "social_account",
                    "value": soc['url'].strip(),
                    "network": network,
                }
            social_row.append(id)
        return social_row

    @check_spider_pipeline
    def process_item(self, item, spider):
        title = ''.join(item['title']).strip()
        url = item['url']
        id = item['id']

        ontoid = u"ext_biletix_people_group_{0}".format(id)

        row = {}

        row["ontoid"] = ontoid

        row["Title"] = [{
            "value": title,
            "langua": "tr"
        }]

        url_info = {
            "type": "url",
            "value": item['url'],
            "langua": "tr"
        }

        social = item['social']
        ids = []
        if social:
            ids = self.make_socials_row(social)
        ids.append(url_info)
        row["ids"] = ids

        row["Projects"] = [{
            "value": u"[[#ext_biletix_etkinlik_{0}]]".format(id),
        }]

        row["isa"] = {
            "otype": [{
                "value": "Hum",
                "subvalue": item['category']
            }],
            "Genres": [{
                "value": item['subcategory'],
                "langua": "tr"
            }]
        }

        sout.write(json.dumps(row, ensure_ascii=False) + "\n")


class EventPipeline(JsonPipeline):
    @check_spider_pipeline
    def process_item(self, item, spider):
        title = ''.join(item['title']).strip()
        init_date = ''.join(item['init_date'])
        time_data = init_date.split("T")

        prices = item['price']
        description = ''.join(item['description'])
        description = self.delete_tags(description).strip()

        row = {}

        row["ontoid"] = u"ext_biletix_etkinlik_{0}".format(item['id'])

        row["Title"] = [{
            "value": title,
            "langua": "tr"
        }]

        row["InitDate"] = [{"value": time_data[0]}]

        images = []
        for img in item['images']:
            image = {
                "src": [{"url": item['url']}],
                "value": img,
                "url": img
            }
            images.append(image)

        if images:
            row["Image"] = images
        participants_text = "[[#ext_biletix_etkinlik_{0}]]".format(item['id'])
        row["Participants"] = [{"value": participants_text}]

        row["ids"] = [{
            "type": "url",
            "value": item['url'],
            "langua": "tr"
        }]

        row["isa"] = {}

        if u"MUSIC" in item['category'] or u"SPORT" in item['category']:
            subvalue = u"СultureEvent@on"
            if u"SPORT" in item['category']:
                subvalue = u"SportEvent@on"

            row["isa"]["otype"] = [{
                "value": "Event",
                "subvalue": subvalue
            }]
        else:
            row["isa"]["otype"] = "Event"

        row["isa"] = {
            "Genres": [{
                "value": "Pop",
                "langua": "tr"
            }]
        }

        if description:
            row["isa"]["Defin"] = [{
                "value": description,
                "langua": "tr"
            }]

        row["params"] = {}
        if time_data[1]:
            time_data_text = time_data[1].replace("::",":")
            time_row = [{"value": time_data_text}]
            row["params"]["Time"] = time_row

        prices_row = []
        if prices:
            for pr in prices:
                price = {
                    "value": pr['price'],
                    "comment": pr['comment'],
                    "langua": "tr"
                }
                prices_row.append(price)

        if prices_row:
            row["params"]["Price"] = prices_row

        sout.write(json.dumps(row, ensure_ascii=False) + "\n")
