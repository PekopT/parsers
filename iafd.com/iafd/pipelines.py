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

    @check_spider_close
    def close_spider(self, spider):
        sout = getwriter("utf8")(stdout)
        sout.write(json.dumps(self.data, ensure_ascii=False) + "\n")


class IafdActorsPipeline(JsonPipeline):

    def check_no_data(self, value):
        if value.strip() == "No data":
            return ''
        else:
            return value

    @check_spider_pipeline
    def process_item(self, item, spider):
        name = self.validate_str(item['name'])
        url = item['url']
        init_place = ''.join(item['init_place'])
        init_date = ''.join(item['init_date'])
        end_date = ''.join(item['end_date'])
        years = ''.join(item['end_date']).strip()
        image = item['image'][0]

        haircolors = item['hair_colors']
        weight = ''.join(item['weight'])
        height = ''.join(item['height'])
        ethnicity = ''.join(item['ethnicity'])
        nationality = ''.join(item['nationality'])


        nationality = self.check_no_data(nationality)
        init_place = self.check_no_data(init_place)
        ethnicity = self.check_no_data(ethnicity)



        wm = re.search(u"\(.+\)", weight)
        if wm:
            weight = wm.group(0)
            weight = re.sub('\D', '', weight)
        else:
            weight = ''

        hm = re.search(u"\(.+\)", height)
        if hm:

            height = hm.group(0)
            height = re.sub(u'\D', u'', height)
        else:
            height = ''


        udm = re.search(u"gender.+", url)

        if udm:
            url_data_search = udm.group(0)

        url_data = url_data_search.split('/')
        male = url_data[0][-1:]

        row = {}

        row['ontoid'] = u"ext_iafd_{0}_{1}".format(male, url_data[1])

        if male.lower == "m":
            profession = u"порноактер"
        else:
            profession = u"поноактрисса"

        ids = []

        ids_url = {}
        ids_url[u"type"] = u"url"
        ids_url[u"value"] = url
        ids_url[u"langua"] = u"en"
        ids.append(ids_url)

        row[u"ids"] = ids

        row[u"Title"] = [
            {
                u"value": name,
                u"langua": u"en"
            }
        ]

        if init_place:
            row[u"InitPlace"] = [
                {
                    u"value": init_place,
                    u"langua": u"en"
                }
            ]

        if init_date:
            row[u"InitDate"] = [
                {
                    u"value": init_date,
                }
            ]
        if end_date:
            row[u"EndDate"] = [
                {
                    u"value": end_date,
                }
            ]

        performer = ''.join(item['performer'])

        row["params"] = {}

        if haircolors:
            row["params"]["HairColor"] = [
                {
                    "value": haircolors,
                    "langua": "en",
                }
            ]
        if weight:
            row["params"]["Weight"] = [
                {
                    "value": weight,
                    "unit": "kg",
                }
            ]

        if height:
            row["params"]["Height"] = [
                {
                    "value": height,
                    "unit": "m",
                }
            ]

        if ethnicity:
            row["params"]["Ethnicity"] = [
                {
                    "value": ethnicity,
                    "langua": "en",
                }
            ]

        row["isa"] = {}
        row["isa"]["Profession"] = [
            {
                "value": profession,  # для f или "порноактер" для m
                "langua": "ru"
            }
        ]

        if nationality:
            row["isa"]["Nationality"] = [
                {
                    "value": nationality,  # для f или "порноактер" для m
                    "langua": "en"
                }
            ]

        row["isa"]["otype"] = [
            {
                "value": "Hum"
            }
        ]

        row["isa"]["tags"] = [
            {
                "value": "Pornoactor@on"
            }
        ]

        if image:
            row['Image'] = [
                {
                    "src": [
                        {
                            "url": url,
                        }
                    ],
                    "value": image,
                    "url": image,
                }
            ]

        if years:
            row['Years'] = [
                {
                    "value": years,
                }
            ]

        row['Key'] = [
            {
                "value": performer,
                "langua": "en",
            }
        ]

        if male.lower() == 'm':
            gender = 'male'
        else:
            gender = 'female'

        row[u'Gender'] = [{u"value": gender}]

        projects = item['projects']

        if projects:
            row['projects'] = projects

        self.data.append(row)


class IafdTitlePipeline(JsonPipeline):
    @check_spider_pipeline
    def process_item(self, item, spider):
        name = self.validate_str(item['name']).strip(': ,.')
        name = name.capitalize()
        url = item['url']
        release_date = self.validate_str(item['release_date']).strip()
        duration = ''.join(item['duration'])
        duration = re.sub('\D', '', duration)
        if duration:
            duration = int(duration) * 60
        else:
            duration = 0
        year = u""
        m = re.search("year\=[\d]+", url)
        if m:
            year = re.sub('\D', '', m.group(0))

        url_data = url.rstrip('/').split('/')
        sub = url_data[-1:][0][0:-4]

        director = item['director']
        studio = item['studio']
        distributor = item['distributor']
        actors = item['actors']
        participants = []

        for act in actors:
            participants.append(act)

        if len(director) > 0:
            participants.append(director)

        if len(studio) > 0:
            participants.append(studio)

        if len(distributor) > 0:
            participants.append(distributor)

        ontoid = u"ext_iafd_film_" + sub[1:-4]

        row = {
            "ontoid": ontoid,
            "ids": [
                {
                    "type": "url",
                    "value": url,
                    "langua": "en"
                }
            ],
            "Title": [
                {
                    "value": name,
                    "langua": "en"
                }
            ],
            "InitDate": [
                {
                    "value": year,
                }
            ],


            "isa": {
                "tags": [
                    {
                        "value": "Porno@on"
                    }
                ],
                "otype": [
                    {
                        "value": "Film"
                    }
                ]
            },
            "params": {
                "Duration": [
                    {
                        "value": duration,
                    }
                ],
                "AgeLimit": [
                    {
                        "value": "18"
                    }
                ]
            }

        }

        release_date = release_date.replace("No Data","").strip()

        if release_date:
            row["ReleaseDate"] = [{"value": release_date,}]

        row["Participants"] = participants
        self.data.append(row)


class IafdDistributorPipeline(JsonPipeline):
    @check_spider_pipeline
    def process_item(self, item, spider):
        name = item['name'].strip(': ,.')
        name = name.capitalize()
        url = item['url']
        related = item['related']

        row = {
            "ontoid": "ext_iafd_studio_stagliano-productions",
            "ids": [
                {
                    "type": "url",
                    "value": url,
                    "langua": "en"
                },
            ],
            "Title": [
                {
                    "value": name,
                    "langua": "en",
                }
            ],
            "rels": {
                "Related": related,
            },
            "isa": {
                "tags": [
                    {
                        "value": "Porno@on"
                    }
                ],
                "otype": [
                    {
                        "value": "Org",
                        "subvalue": "Main@on"
                    }
                ]
            }

        }

        self.data.append(row)


class IafdStudioPipeline(JsonPipeline):
    @check_spider_pipeline
    def process_item(self, item, spider):
        name = item['name'].strip(': ,.')
        name = name.capitalize()
        url = item['url']
        related = item['related']

        row = {
            "ontoid": "ext_iafd_studio_stagliano-productions",
            "ids": [
                {
                    "type": "url",
                    "value": url,
                    "langua": "en"
                },
            ],
            "Title": [
                {
                    "value": name,
                    "langua": "en",
                }
            ],
            "rels": {
                "Related": related,
            },
            "isa": {
                "tags": [
                    {
                        "value": "Porno@on"
                    }
                ],
                "otype": [
                    {
                        "value": "Org",
                        "subvalue": "Main@on"
                    }
                ]
            }

        }

        self.data.append(row)
