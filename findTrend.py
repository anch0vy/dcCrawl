# -*- coding: utf-8 -*-
"""최근 n시간동안의 글들을 분석해서 트랜드를 찾아준다

Usage:
    findTrend.py <gallery> [--debug]
"""
import time
from collections import Counter
from konlpy.tag import Twitter
from db import Category, Session, Article


class Trend:
    def __init__(self, gallery):
        self.gallery = gallery
        self.s_tag = Twitter()
        self.s_db = Session()
        self.filterKeyword = []
        self.filterKeyword.append(u'굴림')
        self.filterKeyword.append(u'존나')

        result = self.s_db.query(Category.id).filter(Category.name == gallery)
        if result.count():
            self.categoryId = result[0][0]
        else:
            raise RuntimeError('No Category')

    def getNouns(self, text):
        return self.s_tag.nouns(text)

    def getTrend(self, timelimit=60 * 60):
        # TODO: 나중에 글 하나에 있는 단어로 md5처리한후 이걸가지고 비슷한 문서 검색해서 중복글 제거
        c = Counter()
        result = self.s_db.query(Article.title, Article.content).filter(Article.timestamp > time.time() - timelimit)
        for title, content in result:
            words = set()
            words.update(self.getNouns(title))
            words.update(self.getNouns(content))
            c.update(list(words))
        for text, n in c.most_common(100):
            if text in self.filterKeyword:
                continue
            if len(text) == 1:
                continue
            print n, text

if __name__ == '__main__':
    from docopt import docopt
    arg = docopt(__doc__)
    trend = Trend(arg['<gallery>'])
    trend.getTrend()
