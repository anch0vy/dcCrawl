def checkDelete(html) :
	breakList = getArticleNumbersFromList(html)
	# 페이지의 글 넘버 리스트를 반환 받음
	first = breakList[0]
	last = breakList[-1]
	# 각각의 첫번째, 마지막 넘버
	for notice in range(first, last) :
		if session.query(Article).filter(Article.id == notice).count() is not 0 :
			# Article.id 에 같은 넘버가 있으면 삭제 안된 것
			continue
		else :
			session.update(Article).where(Article.id == notice).value(isDelete = 1)
			# 없으면 삭제되었으니 isDelete 값 변경