import utils
import random
import pickle
import os
import glob
import wikipediaapi
title = "titre"
sum = "ini□t txt init"
start = "start ini"

def rand(list) :
    return random.choice( list )


def get_wiki():
    global title
    global sum
    global start
    old = title
    art = rand(list(articles.values()))
    if art is not None:
        title = art["title"]
        start = "start" # art.start
        sum = art["summary"].replace('\n',' ')
        print("WIKI : " + art["title"] )
        # print("WIKI : " + art.displaytitle )
        print(start[0:60])
    if old == title : get_wiki()

def get_wiki_langs():
    global langs
    langs = glob.glob(utils.path("files/wiki/articles_*"))
    langs = [s.split('_')[-1] for s in langs]
    return langs

def set_wiki_lang(l):
    global lang
    global articles
    lang = l
    with open(utils.path("files/wiki/articles_"+lang), "rb") as file:
        articles = pickle.load(file)
    get_wiki()
