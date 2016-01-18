# -*- coding: utf-8 -*-
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Setting(Base):
    __tablename__ = 'settings'
    name = Column(String(50), primary_key=True)
    value = Column(String(50))

class Status(Base):
    __tablename__ = 'statuses'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    value = Column(String(50))

class Article(Base):
    __tablename__ = 'articles'
    id = Column(Integer, primary_key=True)
    category = Column(Integer, primary_key=True)
    writer = Column(String(300))
    ip = Column(String(100), nullable=True)
    title = Column(String(300))
    content = Column(String(1000))
    timestamp = Column(Integer)
    isDelete = Column(Boolean())

class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(300))

class Error(Base):
    __tablename__ = 'error'
    id = Column(Integer, primary_key=True)
    articleId = Column(Integer, nullable=True)
    sometext = Column(String(2000), nullable=True)


engine = create_engine('sqlite:///test.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# session = Session()
# if session.query(Category).count() == 0:
#     category = Category(id=0, name=u'분류안됨')
#     session.add(category)
#     category = Category(id=1, name=u'휴지통')
#     session.add(category)
#     session.commit()
# session.close()