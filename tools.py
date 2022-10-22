import datetime
import pymongo
import streamlit as st


def init_connection():
    return pymongo.MongoClient(**st.secrets["mongo"])


def pretty_date(cadena):
    date = cadena.split(".")
    date[0] = "20"+date[0]
    d = datetime.date(int(date[0]), int(date[2]), int(date[1]))
    return d


def request(peticion):
    client = init_connection()
    videos = client["Estadisticas"]["Videos"]

    return videos.find(peticion)


def translate_category_by_id(id):
    client = init_connection()
    cats = client["Estadisticas"]["Videos_Id"]
    dic = cats.find_one({"category_id": id})

    return dic["video_type"]


def translate_category_by_name(name):
    client = init_connection()
    cats = client["Estadisticas"]["Videos_Id"]
    dic = cats.find_one({"video_type": name})

    return dic["category_id"]


if __name__ == '__main__':
    client = init_connection()
    cats = client["Estadisticas"]["Videos_id"]

    print(cats.find({"category_id": 10}))
