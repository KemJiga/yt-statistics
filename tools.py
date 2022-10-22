import datetime
import pymongo
import streamlit as st


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

    return dic["video_type"]


def translate_category_by_name(name):
    client = init_connection()
    cats = client["Estadisticas"]["Videos_Id"]
    dic = cats.find_one({"video_type": name})

    return int(dic["category_id"])


if __name__ == '__main__':
    c = pretty_date("2017/11/14")
    print(c)
