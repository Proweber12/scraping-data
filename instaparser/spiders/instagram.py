import json
import re
from copy import deepcopy
from urllib.parse import urlencode

import scrapy
from scrapy.http import HtmlResponse
from scrapy.loader import ItemLoader

from instaparser.items import InstagramparserItem


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['www.instagram.com']
    start_urls = ['http://www.instagram.com/']
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    inst_login = "bezyn4uk777"
    inst_pwd = "#PWD_INSTAGRAM_BROWSER:10:1648626124:AQ5QAH+xzWyVhI7NSE+deuvPpOWILHr8BYN7nfV3S2pYYIMNjj/vXjjlnH+ELZhTPGu11Cew4K1anXlZbx48PmeE2HEqmiv7DxxIN/BJoPe8eIjdIOABBgOpY7u3IXJlSoObdeSpBGXwn41IDS/7ImamiQ=="
    parse_user = 'techskills_2022'
    followers_list_url = 'https://www.instagram.com/api/v1/friendships/'
    page_count = 0
    max_pages = 20  # Чтоб не всё парсило, слишком долго, но если надо можно убрать

    def parse(self, response: HtmlResponse):
        csrf = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.inst_login_link,
            method='POST',
            callback=self.login,
            formdata={'username': self.inst_login, 'enc_password': self.inst_pwd},
            headers={'X-CSRFToken': csrf}
        )

    def login(self, response: HtmlResponse):
        json_body = json.loads(response.text)
        if json_body['authenticated']:
            yield response.follow(f'/{self.parse_user}', callback=self.connection_type_parse,
                                  cb_kwargs={'username': self.parse_user})

    def connection_type_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        variables = {'count': 12, 'search_surface': 'follow_list_page'}
        url_followers = f'{self.followers_list_url}{user_id}/followers/?{urlencode(variables)}'

        yield response.follow(url_followers,
                              headers={'User-Agent': 'Instagram 87.249.132.213'},
                              callback=self.user_data_parse,
                              cb_kwargs={'username': username,
                                         'user_id': user_id,
                                         'connection_type': 'followers',
                                         'variables': deepcopy(variables)
                                         }
                              )

        url_following = f'{self.followers_list_url}{user_id}/following/?{urlencode(variables)}'

        yield response.follow(url_following,
                              headers={'User-Agent': 'Instagram 87.249.132.213'},
                              callback=self.user_data_parse,
                              cb_kwargs={'username': username,
                                         'user_id': user_id,
                                         'connection_type': 'following',
                                         'variables': deepcopy(variables)
                                         }
                              )

    def user_data_parse(self, response: HtmlResponse, username, user_id, connection_type, variables):
        json_data = json.loads(response.text)
        users = json_data.get('users')
        for user in users:
            loader = ItemLoader(item=InstagramparserItem(), response=response)
            loader.add_value('user_id', user_id)
            loader.add_value('username', username)
            loader.add_value('user_photo', user.get('profile_pic_url'))
            loader.add_value('connection_type', connection_type)
            yield loader.load_item()

        next_page = json_data.get('next_max_id')
        self.page_count += 1
        if next_page and self.page_count <= self.max_pages:
            variables['max_id'] = next_page
            url = f'{self.followers_list_url}/{user_id}/{connection_type}/?{urlencode(variables)}'

            yield response.follow(
                url,
                callback=self.connection_type_parse,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'connection_type': connection_type,
                           'variables': deepcopy(variables)
                           }
            )

    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    def fetch_user_id(self, text, username):
        try:
            matched = re.search('{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text).group()
            return json.loads(matched).get('id')
        except:
            return re.findall('\"id\":\"\\d+\"', text)[-1].split('"')[-2]
