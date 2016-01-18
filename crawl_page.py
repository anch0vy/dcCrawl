# -*- coding: utf-8 -*-
"""dcinside crawler

Usage:
    crawl_page.py <gallery> [<startPage> <endPage>] [--debug]
"""
import requests
import re
import time
import datetime
from db import Session, Article, Category, Error

USERAGENT = 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0'
REFERER = 'http://gall.dcinside.com/board/lists/?id=%s'
ARTICLE_URL = 'http://gall.dcinside.com/board/view/?id=%s&no=%d'


def getStartArticleId(html):
    '''페이지의 가장 위에있는 글의 id를 리턴함
    gallery가 있는지 체크용으로도 쓰임
    '''
    m = re.search('<td class="t_notice" >([0-9]*)</td>', html)
    if m is None:
        return None
    return int(m.group(1))


def parseArticle(html):
    '''게시물을 파싱해서 writer, ip, title, content, time 순으로 리턴함
    content는 html코드(text처리는 트랜드 검색 에서만)
    '''
    m_writer = re.search('<meta name="author" content="(.*)">', html)
    m_title = re.search(u'<meta name="title" content="(.*) - (.*) 갤러리">', html)
    m_ip = re.search('<li class="li_ip">(.*)</li>', html)
    m_content = re.search('<table border="0" width="100%"><tr>(.*)</tr></table>', html, re.DOTALL)
    m_time = re.search('<li><b>(.*)</b></li>', html)
    if not all([m_writer, m_title, m_content, m_time]):
        print [m_writer, m_title, m_content, m_time]
        raise RuntimeError('article parse error')
    writer, ip, title, content, time = map(lambda x: x.group(1), [m_writer, m_ip, m_title, m_content, m_time])
    return writer, ip, title, content, time


def getArticleNumbersFromList(html):
    '''글 목록 화면 html을 넘기면 글 id 리스트를 int형 리스트로 리턴'''
    m = re.findall('<td class="t_notice" >([0-9]*)</td>', html)
    ids = map(int, m)
    return ids


class Crawl:
    def __init__(self, gallery, debug=False):
        '''debug: True면 디버그용 문자열 출력'''
        self.debug = debug
        self.gallery = gallery
        self.galleryUrl = 'http://gall.dcinside.com/board/lists/?id=%s&page=%d'

        self.idSet = set()  # db넣기전 1차 id 체크용

        self.s_db = Session()
        if self.s_db.query(Category).filter(Category.name == self.gallery).count() == 0:
            category = Category()
            category.name = self.gallery
            self.s_db.add(category)
            self.s_db.commit()
            self.categoryId = category.id
        else:
            id, = self.s_db.query(Category.id).filter(Category.name == self.gallery)[0]
            self.categoryId = id

        headers = {}
        headers['User-Agent'] = USERAGENT
        headers['Accept-Language'] = 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3'
        headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        headers['Referer'] = REFERER % self.gallery
        self.s_req = requests.Session()
        self.s_req.headers.update(headers)

    def add2db(self, id, writer, ip, title, content, time_):
        '''디비에 넣는다.
        이미 존재하는지 체크를 하고 리턴값은 항상 None
        '''
        check = self.s_db.query(Article).filter((Article.id == id) & (Article.category == self.categoryId)).count()
        if check > 0:
            return
        timestamp = time.mktime(datetime.datetime.strptime(time_, "%Y-%m-%d %H:%M:%S").timetuple())
        article = Article()
        article.id = id
        article.content = content
        article.writer = writer
        article.ip = ip
        article.title = title
        article.timestamp = timestamp
        article.category = self.categoryId
        article.comment = 0
        article.isDelete = False
        self.s_db.add(article)
        self.s_db.commit()
        if self.debug:
            try:
                print '[add]', id, ':', int(time.time()) - int(timestamp), title
            except:
                print '[error]debug print error'
                self.debug = False
        return

    def crawlOnePage(self, page):
        '''페이지 한개에 있는 글들을 크롤링한다.'''
        r = self.s_req.get(self.galleryUrl % (self.gallery, page))
        id = getStartArticleId(r.text)
        if id is None:
            raise RuntimeError('[error]wrong gall')

        r = self.s_req.get(self.galleryUrl % (self.gallery, page))
        ids = getArticleNumbersFromList(r.text)
        for id in ids:
            if id in self.idSet:
                continue
            self.idSet.add(id)
            try:
                r = self.s_req.get(ARTICLE_URL % (self.gallery, id))
                writer, ip, title, content, time_ = parseArticle(r.text)
                self.add2db(id, writer, ip, title, content, time_)
            except Exception as e:
                error = Error()
                error.articleId = id
                error.sometext = str(e)
                print '[error]', error.sometext
                self.s_db.add(error)
                self.s_db.commit()

if __name__ == '__main__':
    from docopt import docopt
    arg = docopt(__doc__)

    if arg['<gallery>'] and arg['<startPage>'] and arg['<endPage>']:
        # 특정 페이지만 크롤링
        crawl = Crawl(arg['<gallery>'], arg['--debug'])
        startPage = int(arg['<startPage>'])
        endPage = int(arg['<endPage>'])
        for n in range(startPage, endPage + 1):
            if arg['--debug']:
                print '[info]page:', n
            crawl.crawlOnePage(n)

    elif arg['<gallery>']:
        # 1페이지 계속 크롤링
        crawl = Crawl(arg['<gallery>'], arg['--debug'])
        while True:
            crawl.crawlOnePage(1)
            time.sleep(5)
