# -*- coding: utf-8 -*-
import scrapy
import base64
import io
import re
from scrapy.selector import Selector
from spider_58city.items import Spider58CityItem
from fontTools.ttLib import TTFont


class MainSpider(scrapy.Spider):
    """51同城爬虫"""
    name = "58city"
    allowed = ["www.58.com"]
    start_urls = ["https://www.58.com/changecity.html"]

    def parse(self, response):
        """
        解析城市切换页面,并生成城市租房页面 url
        """
        data = response.xpath("//script[3]/text()").extract_first()
        city_list =re.findall(r':"(.*?)\|.*?"',data)
        url_temp = "https://{}.58.com/chuzu/"
        url_list = [url_temp.format(city) for city in city_list]
        # with open('./text.txt','w',encoding='utf-8') as f:
        #         f.write(response.text)
        for url in url_list[0:1]:
            yield scrapy.Request(url=url,callback=self.parse_house_list)

    def parse_house_list(self, response):
        """
        在租房页面，解析广告标题和租房价格
        """
        with open('./text.txt','w',encoding='utf-8') as f:
                f.write(response.text)
        new_response = self.cracking_font_encryption(response)
        li_list = new_response.xpath("//li[@class='house-cell']")
        item = Spider58CityItem()
        for li in li_list[0:3]:
            item["title"] = li.xpath("./div[2]/h2/a/text()").extract_first().strip()
            item["price"] = li.xpath("./div[3]/div[2]/b/text()").extract_first()
            yield item



        # print(response.text)

    def cracking_font_encryption(self, response):
        """
        应对字体反爬
        :param response: scrapy返回的response
        :return: 破解字体反爬后的response
        """
        # 抓取加密字符串
        base64_str = response.xpath('//head/script[position()=2]/text()').re(r"base64,(.*?)'\) format")[0]
        b = base64.b64decode(base64_str)
        # print(b)
        font = TTFont(io.BytesIO(b))

        bestcmap = font['cmap'].getBestCmap()
        # print(bestcmap)
        newmap = dict()  # 计算正常字体的映射字典
        for key in bestcmap.keys():
            value = int(re.search(r'(\d+)', bestcmap[key]).group(1)) - 1
            key = hex(key)
            # print(key)
            newmap[key] = value

        response_ = response.text  # 根据映射字典替换反爬字符
        for key, value in newmap.items():

            key_ = key.replace('0x', '&#x') + ';'
            # print(key,'   ',key_)
            if key_ in response_:
                response_ = response_.replace(key_, str(value))

        # text = response_
        return Selector(text=response_)  # 得到破解后的新response