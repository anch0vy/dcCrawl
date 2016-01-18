# -*- coding: utf-8 -*-
"""최근 n시간동안의 글들을 분석해서 트랜드를 찾아준다

Usage:
    findTrend.py <gallery> [--debug]
"""

from konlpy.tag import Twitter
from db import Category, Session, Article


class Trend:
    def __init__(self, gallery):
        self.gallery = gallery
        self.s_tag = Twitter()
        self.s_db = Session()

    def getNouns(self, text):
        return self.s_tag.nouns(text)

if __name__ == '__main__':
    from docopt import docopt
    arg = docopt(__doc__)
    trend = Trend(arg['<gallery>'])
