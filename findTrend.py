# -*- coding: utf-8 -*-
"""최근 n시간동안의 글들을 분석해서 트랜드를 찾아준다

Usage:
    findTrend.py <gallery> [--debug]
"""
import time
import datetime
import numpy as np
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
        result = self.s_db.query(Article.title, Article.content).filter(
            (Article.timestamp > time.time() - timelimit) &
            (Article.category == self.categoryId)
            )
        for title, content in result:
            words = set()
            words.update(self.getNouns(title))
            words.update(self.getNouns(content))
            words = filter(lambda x: len(x) > 1, words)
            c.update(list(words))
        for text, n in c.most_common(100):
            if text in self.filterKeyword:
                continue
            if len(text) == 1:
                continue
            self.filterKeyword.append(text)

    def spamCount(self, word):
        '''특정사용자가 어떤 키워드를 30%이상 차지하고있으면 스팸일 가능성이 높기에 그만큼 값을 빼준다.'''
        c = Counter()
        word = u'%%%s%%' % word
        result = self.s_db.query(Article.title, Article.content).filter(
            (Article.timestamp > time.time() - timelimit) &
            (Article.category == self.categoryId)
            )
        for writer, ip in result:
            if writer and ip == '':
                id = writer
            else:
                id = ip
            c[id] += 1
        ret = 0
        sum_all = sum(map(lambda key: c[key], c))
        for key, count in c.most_common(10):
            per = float(count) / sum_all
            if per > 0.3:
                print '%-20s\t%0.3f' % (key, per)
                ret += count
        return ret

    def trendDraw(self, words, filename):
        '''각 단어들의 빈도를 30분 간격으로 조사해서 그래프로 그려준다.
        '''
        import matplotlib
        matplotlib.use('Agg')  # 무조건 임포트다음에 바로 써줘야한다
        import matplotlib.pyplot as plt
        matplotlib.rc('font', family='DungGeunMo')
        # 만약 문제가있을때 DungGeunMo폰트를 ~/.fonts폴더에 넣고  fc-cache -f -v실행한후 ~/.cache/matplotlib 폴더를 날려보자
        plt.rcParams["figure.figsize"] = 15, 5
        cBase = Counter()
        # 그래프 그릴때 미리 전부 0으로 셋팅안해두면 의도한대로 그래프가 안그려짐
        for time_ in range(int(time.time() - 60 * 60 * 24), int(time.time() - 60 * 60)):
            tmp = datetime.datetime.fromtimestamp(time_ - time_ % (60 * 30))
            cBase[tmp] = 0

        for word in words:
            c = cBase.copy()
            likeword = '%%%s%%' % word
            for time_, in self.s_db.query(Article.timestamp).filter(
                (Article.title.like(likeword) | Article.content.like(likeword)) &
                (Article.category == self.categoryId) &
                (Article.timestamp > time.time() - 60 * 60 * 24) &
                (Article.timestamp < time.time() - 60 * 60)
                ):
                hour = datetime.datetime.fromtimestamp(time_ - time_ % (60 * 30))
                c[hour] += 1
            l = c.items()
            l.sort()

            data = map(lambda x: x[1], l)[-2:]
            x = np.arange(0,len(data))
            y = np.array(data)
            z = np.polyfit(x,y,1)
            tag = str(z)

            plt.plot(map(lambda x: x[0], l), map(lambda x: x[1], l), '-', label=word)

        plt.xlabel(u'시간')
        plt.ylabel(u'글갯수')
        plt.title(tag)
        plt.legend(words)
        plt.savefig(filename, dpi=(640))
        plt.clf()

    def getTrend(self, timelimit=60 * 30):
        '''트랜드를 구해준다... 미완성

        TODO
            트랜드에 영향을 끼치는값
            최근에 이게 핫해지기 시작했는가?
            근데 이거 구하려면 30분 ~ 1시간으로 나눠서 추세를 봐야함
            근데 또 추세를 볼때 그냥보면 안되고 (키워드가 포함된 글) / (그 해당 시간구간에 올라온 글) 값으로 추세를 구해야할것같음
        '''
        c = Counter()
        result = self.s_db.query(Article.title, Article.content).filter(
            (Article.timestamp > time.time() - timelimit) &
            (Article.category == self.categoryId)
            )
        for title, content in result:
            words = set()
            words.update(self.getNouns(title))
            words.update(self.getNouns(content))
            words = list(words)
            words = filter(lambda x: len(x) > 1, words)
            c.update(words)

        for word, n in c.most_common(100):
            tmp = self.test(word)
            if tmp[0] > 1.5:
                print word, n, tmp
            if n == 1:
                break

    def test(self, word):
        result = []
        likeword = '%%%s%%' % word
        startTime = int(time.time() - 60 * 60 * 24)
        midTime = int(time.time() - 60 * 30)
        t1 = self.s_db.query(Article).filter(
            (Article.timestamp >= startTime) &
            (Article.timestamp <= midTime) &
            (Article.category == self.categoryId) &
            (Article.title.like(likeword) | Article.content.like(likeword))
            ).count()
        t1_entire = self.s_db.query(Article).filter(
            (Article.timestamp >= startTime) &
            (Article.timestamp <= midTime) &
            (Article.category == self.categoryId)
            ).count()
        t2 = self.s_db.query(Article).filter(
            (Article.timestamp >= midTime) &
            (Article.category == self.categoryId) &
            (Article.title.like(likeword) | Article.content.like(likeword))
            ).count()
        t2_entire = self.s_db.query(Article).filter(
            (Article.timestamp >= midTime) &
            (Article.category == self.categoryId)
            ).count()
        try:
            t1_per = t1 / float(t1_entire)
            t2_per = t2 / float(t2_entire)
            return t2_per / t1_per, t2_per, t1_per
        except:
            return 100, None

if __name__ == '__main__':
    from docopt import docopt
    # now = time.time()
    # def mytime():
    #     return now - 60 * 60 * 10
    # time.time = mytime
    arg = docopt(__doc__)
    trend = Trend(arg['<gallery>'])
    trend.getTrend()