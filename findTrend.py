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
    '''Trend가져오는 클래스
    
    주의사항
    sqlite에서 하면 db에 락이 걸리기 때문에 db사용불가능
    따라서 crawl_page.py가 돌아가고 있을때 스크립트 사용 비추천(mysql에서는 OK)
    '''
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

    def findCommonWord(self, timelimit=60 * 60 * 24 * 3):
        '''최근 몇일동안 있었던 글에서 가장 자주나오는 단어들을 찾음
        이 단어들은 항상 자주 쓰이는 단어들이므로 제거
        '''
        c = Counter()
        result = self.s_db.query(Article.title, Article.content).filter(Article.timestamp > time.time() - timelimit)
        for title, content in result:
            words = set()
            words.update(self.getNouns(title))
            words.update(self.getNouns(content))
            words = filter(lambda x:len(x)>1, words)
            c.update(list(words))
        for text, n in c.most_common(20):
            if text in self.filterKeyword:
                continue
            if len(text) == 1:
                continue
            self.filterKeyword.append(text)

    def spamCount(self, word):
        '''특정사용자가 어떤 키워드를 30%이상 차지하고있으면 스팸일 가능성이 높기에 그만큼 값을 빼준다.'''
        c = Counter()
        word = u'%%%s%%' % word
        result = self.s_db.query(Article.writer, Article.ip).filter(Article.title.like(word) | Article.content.like(word))
        for writer, ip in result:
            if writer and ip == '':
                id = writer
            else:
                id = ip
            c[id] += 1
        ret = 0
        sum_all = sum(map(lambda key:c[key], c))
        for key, count in c.most_common(10):
            per = float(count)/sum_all
            if per > 0.3:
                print '%-20s\t%0.3f'%(key, per)
                ret += count
        return ret

    def trendDraw(self, words):
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        matplotlib.rc('font', family='DungGeunMo')
        for word in words:
            c = Counter()
            for x in range(24):
                c[x] = 0
            likeword = '%%%s%%' % word
            for time_, in self.s_db.query(Article.timestamp).filter(
                Article.title.like(likeword) | Article.content.like(likeword) &
                (Article.timestamp > time.time() - 60 * 60 * 24)
                ):
                hour = (time.time() - time_) / 60 / 60
                hour = int(hour)
                c[hour] += 1
            l = c.items()
            plt.plot(map(lambda x:x[0], l), map(lambda x:x[1], l), '.-', label=word)
        plt.xlabel(u'시간')
        plt.ylabel(u'글갯수')
        plt.title(u'???? - by 통계청')
        plt.legend(words)
        plt.savefig("sampleg.png",dpi=(640))

    def getTrend(self, timelimit=60 * 60):
        c = Counter()
        result = self.s_db.query(Article.title, Article.content).filter(Article.timestamp > time.time() - timelimit)
        for title, content in result:
            words = set()
            words.update(self.getNouns(title))
            words.update(self.getNouns(content))
            c.update(list(words))
        tmp = []
        for text, n in c.most_common(100):
            if text in self.filterKeyword:
                continue
            if len(text) == 1:
                continue
            print '============='
            print n, text
            self.spamCount(text)

if __name__ == '__main__':
    from docopt import docopt
    arg = docopt(__doc__)
    trend = Trend(arg['<gallery>'])
    # trend.findCommonWord()
    # print trend.filterKeyword
    # trend.getTrend(60 * 60 * 12)
    trend.trendDraw([u'게임', u'공포', u'삼국지'])