# -*- coding: utf-8 -*-
import os

from flask import Flask, render_template, request
import urllib3
from bs4 import BeautifulSoup
import random

app = Flask(__name__)

MONSTER_NO_MAX=898
IMG_SOURCE_URL='https://zukan.pokemon.co.jp/detail/'

class Monster:
    pass

@app.route("/")
@app.route("/<id>", methods=['GET', 'POST'])
def show(id=None, mistake=False):
    if id is None: id = "{:03d}".format(random.randint(1, MONSTER_NO_MAX))

    print(id)
    url = IMG_SOURCE_URL + str(id)

    http = urllib3.PoolManager()
    r = http.request('GET', url)

    soup = BeautifulSoup(r.data, 'html.parser')
    meta_tag = soup.find_all('meta', attrs={'property': 'og:image'})
    img_url = meta_tag[0].get('content')
    meta_tag = soup.find_all('meta', attrs={'property': 'og:title'})
    name = meta_tag[0].get('content').split(u'｜')[0].split()[0]
    def translate_kana2alphabet(kana):
        map_k2a = {u'ア':'A', u'イ':'I', u'ウ':'U', u'エ':'E', u'オ':'O', u'カ':'KA', u'キ':'KI',u'ク':'KU',u'ケ':'KE',u'コ':'KO',
        u'サ':'SA',u'シ':'SHI',u'ス':'SU',u'セ':'SE',u'ソ':'SO',u'タ':'TA',u'チ':'CHI',u'ツ':'TU',u'テ':'TE',u'ト':'TO',
        u'ナ':'NA',u'ニ':'NI',u'ヌ':'NU',u'ネ':'NE',u'ノ':'NO',u'ハ':'HA',u'ヒ':'HI',u'フ':'FU',u'ヘ':'HE',u'ホ':'HO',
        u'マ':'MA',u'ミ':'MI',u'ム':'MU',u'メ':'ME',u'モ':'MO',u'ヤ':'YA',u'ユ':'YU',u'ヨ':'YO',u'ワ':'WA',u'ヲ':'WO',u'ン':'NN',
        u'ラ':'RA',u'リ':'RI',u'ル':'RU',u'レ':'RE',u'ロ':'RO',
        u'ガ':'GA',u'ギ':'GI',u'グ':'GU',u'ゲ':'GE',u'ゴ':'GO',u'ザ':'ZA',u'ジ':'JI',u'ズ':'ZU',u'ゼ':'ZE',u'ゾ':'ZO',
        u'ダ':'DA',u'ヂ':'DI',u'ヅ':'DU',u'デ':'DE',u'ド':'DO',u'バ':'BA',u'ビ':'BI',u'ブ':'BU',u'ベ':'BE',u'ボ':'BO',
        u'パ':'PA', u'ピ':'PI',u'プ':'PU',u'ペ':'PE',u'ポ':'PO',u'ヴ':'VU',u'ッ':'XTU',u'ャ':'XYA',u'ュ':'XYU',u'ョ':'XYO',
        u'ァ':'XA',u'ィ':'XI',u'ゥ':'XU',u'ェ':'XE',u'ォ':'XO',
        u'ー':'-',u'・':'',u' ':' ',u'♀':'',u'♂':'',u'Ｚ':'Z',u'：': ''}
        alphabets = []
        for char in kana:
            alphabets.append(map_k2a[char])

        # 「ッ」の処理
        for i, alphabet in enumerate(alphabets):
            if alphabet == 'XTU': alphabets[i+1] = alphabets[i+1][0] + alphabets[i+1][:]

        # 「ャ」「ュ」「ョ」の処理
        # 以下、前の子音＋母音でいけるもの KI XYA -> KYA
        # 「キャ」「キュ」「キョ」「シャ」「シュ」「ショ」「チャ」「チュ」「チョ」「ニャ」「ニュ」「ニョ」「ヒャ」「ヒュ」「ヒョ」
        # 「ミャ」「ミュ」「ミョ」「リャ」「リュ」「リョ」「ギャ」「ギュ」「ギョ」「ジャ」「ジュ」「ジョ」「ヂャ」「ヂュ」「ヂョ」
        # 「ビャ」「ビュ」「ビョ」「ピャ」「ピュ」「ピョ」
        for i, alphabet in enumerate(alphabets):
            if alphabet in ('XYA', 'XYU', 'XYO'): 
                if alphabets[i-1] in ('SHI','CHI','JI'):
                    alphabets[i-1] = alphabets[i-1][:-1] + alphabets[i][2]
                else:
                    alphabets[i-1] = alphabets[i-1][:-1] + alphabets[i][1:3]
            elif alphabet in ('XE'):
                if alphabets[i-1] in ('SHI','CHI','JI'):
                    alphabets[i-1] = alphabets[i-1][:-1] + alphabets[i][1]
        
        alphabets = [alphabet for alphabet in alphabets if alphabet not in ('XYA', 'XYU', 'XYO','XE', 'XTU', '')]
        print(alphabets)
        return ' '.join(alphabets)

    alphabets = translate_kana2alphabet(name)

    return render_template('index.html', id=id, img_url=img_url, name=name, alphabets=alphabets, mistake=mistake)

@app.route("/check", methods=['POST'])
def cehck():
    print(request.form.get('input'))
    input = request.form.get('input').replace(' ', '')
    name = request.form.get('alphabets').replace(' ', '')
    id = request.form.get('id')

    if input.lower() == name.lower():
        new_id = "{:03d}".format(random.randint(1, MONSTER_NO_MAX))
        return show(new_id)
    else:
        return show(id, mistake=True)

@app.route("/search")
def search():
    return render_template('search.html')

@app.route("/test")
def test():
    return render_template('test.html')

if __name__ == "__main__":
    #app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
    app.run(debug=True)