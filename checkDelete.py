<<<<<<< HEAD
from db import Article, Session
from crawl_page import getArticleNumbersFromList


def checkDelete(html):
    session = Session()
    breakList = getArticleNumbersFromList(html)
    # 페이지의 글 넘버 리스트를 반환 받음
    first = breakList[0]
    last = breakList[-1]
    # 각각의 첫번째, 마지막 넘버
    for notice in range(first, last):
        if session.query(Article).filter(Article.id == notice).count() is not 0:
            # Article.id 에 같은 넘버가 있으면 삭제 안된 것
            continue
        else:
            session.update(Article).where(Article.id == notice).value(isDelete=1)
            # 없으면 삭제되었으니 isDelete 값 변경
    session.commit()
=======
# -*- coding: utf-8 -*-
from crawl_page import getArticleNumbersFromList
from db import Session, Article
import urllib2
import sys


def checkDelete(html):
    breaklist = getArticleNumbersFromList(html)
    # 페이지의 글 넘버 리스트를 반환 받음
    first = breaklist[0]
    last = breaklist[-1]
    # 각각의 첫번째, 마지막 넘버
    sdb = Session()
    for notice in range(first, last):
        if sdb.query(Article).filter(Article.id == notice).count() is not 0:
            # Article.id 에 같은 넘버가 있으면 삭제 안된 것
            continue
        else:
            sdb.update(Article).where(Article.id == notice).value(isDelete=1)
            print("{} deleted.".format(notice))
            # 없으면 삭제되었으니 isDelete 값 변경

if __name__ == '__main__':
    if len(sys.argv) is 1:
        print("checkDelete.py <gallery>")
        exit(1)
    if isinstance(sys.argv[1], basestring):
        g = sys.argv[1]
    else:
        exit(1)
    opn = urllib2.urlopen("http://gall.dcinside.com/board/lists/?id={}".format(g))
    checkDelete(opn.read())
>>>>>>> refs/remotes/origin/checkDelete
