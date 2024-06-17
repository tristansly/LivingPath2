import wikipediaapi
import iso639
import random
CNS = wikipediaapi.Namespace.CATEGORY
debug = False
def get_rand_article(categorymembers, level=0, max_level=17):
    result = None
    articles = []
    categories = []
    for v in ( categorymembers.values() ) :
        # print(v)
        if (v.ns==0) : articles.append(v)
        if (v.ns==CNS) : categories.append(v)

    if len(categories) > len(articles) and level < max_level :
        c = rand(categories)
        if debug: print("%s: %s (ns: %d) cat:%d, art:%d" % ("*" * (level + 1), c.title, c.ns, len(categories), len(articles) ))
        result = get_rand_article(c.categorymembers, level=level + 1, max_level=max_level)
    elif len(articles) > 0 :
        result = c = rand(articles)
        if debug: print("%s: %s (ns: %d) cat:%d, art:%d" % ("*" * (level + 1), c.title, c.ns, len(categories), len(articles) ))
    else :
        if debug: print("error")
    return result

def rand(list) :
    # return next(iter(list))
    return random.choice( list )

title = "titre"
sum = "ini□t txt init"
wiki_wiki = wikipediaapi.Wikipedia('LivingPath (ivan@mailoo.org)', language="en", extract_format=wikipediaapi.ExtractFormat.WIKI)
top_cat = wiki_wiki.page("Category:Plants")
langs = top_cat.langlinks
# if debug: print("LANG LEN : ", len(langs))
title, sum, start = '','',''
def get_wiki():
    global title
    global sum
    global start
    art = get_rand_article( top_cat.categorymembers )
    if art is not None:
        title = art.title
        start = wiki_wiki.extracts(art, exsentences=1)
        sum = art.summary.replace('\n',' ')
        print("WIKI : " + art.title )
        print("WIKI : " + art.displaytitle )
        print(start[0:60])
        # for a in art.categories : print(a)

def get_wiki_langs():
    for l in langs:
        try:
            langs[l].name = iso639.Language.match(l).name
        except Exception as e:
            langs[l].name = str(l)
    return langs

def set_wiki_lang(l):
    global wiki_wiki
    global top_cat
    global lang
    lang = l
    wiki_wiki = wikipediaapi.Wikipedia('LivingPath (ivan@mailoo.org)', lang)

    if debug: print("SET LANG : "+lang)
    top_cat = wiki_wiki.page( langs[lang].title )
    get_wiki()

# if debug: print(wiki_wiki.page(langs['ace'].title))
# set_wiki_lang('fr')
# get_wiki_langs()
