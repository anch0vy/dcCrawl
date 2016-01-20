# -*- coding: utf-8 -*-
# ci_t, name, password, memo, id, no, best_origin 값x, check_6, check_7, check_8, campus = 0, recomment = 0
# ci_t = md5(time()) 추측
# check_6 = 제목, check_7 = 유동, 고정 나눠지는 듯, check_8 = 닉? (추측)
import getpass
import requests


def write_comment(gallery, no):
    g_id = gallery
    no = no
    name = raw_input("Nickname : ")
    password = getpass.getpass()
    memo = raw_input("""Content :
    """)
    post_param = {
        "ci_t": "0",
        "name": name,
        "password": password,
        "memo": memo,
        "id": g_id,
        "best_origin": "0",
        "check_6": "0",
        "check_7": "0",
        "check_8": "0",
        "campus": "0",
        "recomment": "0"
    }
    r = requests.post("http://gall.dcinside.com/board/lists/?id={}".format(g_id), params=post_param)
    print("{}".format(r.text))
