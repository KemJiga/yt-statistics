import datetime
import pymongo
import streamlit as st
import math


def init_connection():
    return pymongo.MongoClient(**st.secrets["mongo"])


def pretty_date(cadena):
    date = cadena.split("/")
    date[0] = date[0][2:]
    d = date[0] + "." + date[2] + "." + date[1]
    return d


def request(p):
    client = init_connection()
    videos = client["Estadisticas"]["Videos"]

    return videos.find(p)


def translate_category_by_id(id):
    client = init_connection()
    cats = client["Estadisticas"]["Videos_Id"]
    dic = cats.find_one({"category_id": id})
    cat = dic["video_type"]

    return cat


def translate_category_by_name(name):
    client = init_connection()
    cats = client["Estadisticas"]["Videos_Id"]
    dic = cats.find_one({"video_type": name})

    return int(dic["category_id"])


millnames = ['', ' K', ' M', ' B', ' T']


def millify(n):
    n = float(n)
    millidx = max(0, min(len(millnames) - 1,
                         int(math.floor(0 if n == 0 else math.log10(abs(n)) / 3))))

    return '{:.0f}{}'.format(n / 10 ** (3 * millidx), millnames[millidx])


if __name__ == '__main__':
    c = pretty_date("2017/11/14")
    print(c)
