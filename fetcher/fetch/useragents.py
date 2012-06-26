# -*- coding: utf-8 -*-

from random import choice, seed


USER_AGENTS = '''
    Googlebot/2.1 (+http://www.google.com/bot.html)
    Mozilla/5.0 (compatible; googlebot/2.1; +http://www.google.com/bot.html)
    Googlebot-Image/1.0
    gsa-crawler
    YahooFeedSeeker/2.0 (compatible; Mozilla 4.0; MSIE 5.5; http://publisher.yahoo.com/rssguide; users X; views X)
    Mozilla/5.0 (compatible; Yahoo! Slurp;http://help.yahoo.com/help/us/ysearch/slurp) Mozilla/5.0 (compatible; Yahoo! Slurp China; http://misc.yahoo.com.cn/help.html)
    Yahoo!-MMCrawler/3.x (mms dash mmcrawler dash support at yahoo dash inc dot com)
    Mozilla/5.0 (compatible; YandexBot/3.0)
    Mozilla/5.0 (compatible; YandexBot/3.0; MirrorDetector)
    Mozilla/5.0 (compatible; YandexImages/3.0)
    Mozilla/5.0 (compatible; YandexVideo/3.0)
    Mozilla/5.0 (compatible; YandexMedia/3.0)
    Mozilla/5.0 (compatible; YandexBlogs/0.99; robot)
    Mozilla/5.0 (compatible; YandexAddurl/2.0)
    Mozilla/5.0 (compatible; YandexFavicons/1.0)
    Mozilla/5.0 (compatible; YandexDirect/3.0)
    Mozilla/5.0 (compatible; YandexDirect/2.0; Dyatel)
    Mozilla/5.0 (compatible; YandexMetrika/2.0)
    Mozilla/5.0 (compatible; YandexCatalog/3.0; Dyatel)
    Mozilla/5.0 (compatible; YandexNews/3.0)
    Mozilla/5.0 (compatible; YandexImageResizer/2.0)
'''.strip().splitlines()


seed()


def get_user_agent():
    '''Случайный User-Agent'''
    return choice(USER_AGENTS).strip()
