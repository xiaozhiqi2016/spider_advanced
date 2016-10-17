# -*- coding: utf-8 -*-
import json
import urllib

import scrapy
from scrapy.http.request import Request
from project34.items import AgencyItem
from project34.items import CommitItem

class AgencysSpider(scrapy.Spider):
    name = 'AgentcysSpider'
#    start_urls = ['https://kyfw.12306.cn/otn/userCommon/allProvince']

    custom_settings = {
            'ITEM_PIPELINES': {
                'project34.pipelines.AgencySQLPipeline': 300,
            },
#            'DUPEFILTER_DEBUG': True,
            'DUPEFILTER_CLASS': "project34.filter.URLTurnFilter",
    }

    def __init__(self, *a, **kw):
        super(AgencysSpider, self).__init__(self.name, **kw)
        self.turn = a[0]
        self.logger.info("%s. this turn %d" % (self.name, self.turn)) 

    def start_requests(self):
        yield Request("https://kyfw.12306.cn/otn/userCommon/allProvince", callback = self.parse, meta = {"turn":self.turn})

    def parse(self, response):
        url = "https://kyfw.12306.cn/otn/queryAgencySellTicket/query?" 

        j = json.loads(response.body)
        for prov in j["data"]:

            params = {"province":prov["chineseName"].encode("utf-8"), "city":"", "county":""}
            s_url = url + urllib.urlencode(params)

            yield Request(s_url, callback = self.parse_agency, meta = {"turn":response.meta["turn"]})

    def parse_agency(self, response):
        datas = json.loads(response.body)
        for data in datas["data"]["datas"]:
            item = AgencyItem()
            item["province"] = data["province"]
            item["city"] = data["city"]
            item["county"] = data["county"]
            item["address"] = data["address"]
            item["name"] = data["agency_name"]
            item["windows"] = data["windows_quantity"]
            item["start"] = data["start_time_am"]
            item["end"] = data["stop_time_pm"]
            item["turn"] = response.meta["turn"];
            yield item
        yield CommitItem()


