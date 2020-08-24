import scrapy
import json
import pdfkit
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
        data = obj['data']
        for item in data:
            article_id = item['_id']
            title = item["title"]
            cb_kwargs = {"article_id": article_id, "title": title}

            request_url = 'https://gitbook.cn/gitchat/activity/' + article_id
            body = {'activityId': article_id,
                    'requestUrl': request_url,
                    'sceneId': '',
                    'type': 'chat'}

            yield scrapy.Request(url=activity_url,
                                 cookies=self.cookie,
                                 headers=self.headers,
                                 method='POST',
                                 body=json.dumps(body))

            yield scrapy.Request(url=request_url,
                                 callback=self.parse_active_info,
                                 cookies=self.cookie,
                                 headers=self.headers,
                                 cb_kwargs=cb_kwargs)

    def parse_active_info(self, response, article_id, title):
        detail_url = response.css(".buy_btns_view a::attr('href')").extract_first()
        if detail_url is None:
            text = response.css(".buy_btns_view div::text").extract_first()
            print('{} - {}'.format(text, title))
            pass
        else:
            detail_url = 'https://gitbook.cn' + detail_url

            options = {'cookie': []}
            for item in settings.COOKIE.items():
                options['cookie'].append(item)

            config = pdfkit.configuration(wkhtmltopdf=settings.WKHTMLTOPDF_PATH)
            path = './data/{}.pdf'.format(article_id)
            pdfkit.from_url(detail_url, path,
                            configuration=config, options=options)

            pass
