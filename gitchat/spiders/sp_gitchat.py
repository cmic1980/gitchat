import scrapy
import json
from gitchat.items import ArticleItem
import gitchat.settings as settings


class SpGitChat(scrapy.Spider):
    name = 'sp_gitchat'
    allowed_domains = ['gitbook.cn']
    # root_url = 'https://gitbook.cn/activities?page='
    # offset = 1
    start_urls = []

    cookie = settings.COOKIE
    headers = {
        # 保持链接状态
        'Content-Type': 'application/json; charset=UTF-8'
    }

    def __init__(self):
        list_url = 'https://gitbook.cn/activities?page='
        for i in range(settings.MAX_OFFSET):
            self.start_urls.append(list_url + str(i + 1))
            pass

    '''
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url,
                                 callback=self.parse,
                                 cookies=self.cookie,
                                 headers=self.headers)


    def parse(self, response):
        json_content = response.body.decode('utf-8')
        obj = json.loads(json_content)
        data = obj["data"]

        for item in data:
            article = ArticleItem()
            article['id'] = item["_id"]
            article['title'] = item["title"]
            article['description'] = item["description"]
            article['created'] = item["createdAt_str"]

            yield article

            # next page

        if len(data) != 0 and self.offset < settings.MAX_OFFSET:
            self.offset += 1
            yield scrapy.Request(self.root_url + str(self.offset), callback=self.parse)
    '''

    # 获取文章列表
    def parse(self, response):
        for item_url in self.start_urls:
            yield scrapy.Request(item_url, self.parse_active)

    def parse_active(self, response):
        activity_url = 'https://gitbook.cn/m/mazi/vip/order/activity'
        json_content = response.body.decode('utf-8')
        obj = json.loads(json_content)
        data = obj["data"]
        for item in data:
            id = item['_id']
            body = {'activityId': id,
                "requestUrl": "https://gitbook.cn/gitchat/activity/" + id,
                "sceneId": "",
                "type": "chat"}

            yield scrapy.Request(url=activity_url,
                                 callback=self.parse,
                                 cookies=self.cookie,
                                 headers=self.headers,
                                 method='POST',
                                 body= json.dumps(body))
