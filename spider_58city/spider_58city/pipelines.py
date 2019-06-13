# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import redis
class Spider58CityPipeline(object):

    def __init__(self):
        self.db = redis.StrictRedis(host='127.0.0.1', port=6379, decode_responses=True,)
    def process_item(self, item, spider):
        db = self.db
        data = "{}{}".format( item['title'], item['price'])
        db.sadd("58city", data)

        return item
