import urllib, json
from nltk import word_tokenize, pos_tag
from flask import Flask, request, render_template
from markupsafe import Markup
from bs4 import BeautifulSoup

app = Flask(__name__)
options = json.load(open("static/pos.json", "r"))

@app.route('/', methods=['GET', 'POST'])
def index():
  if request.method == 'POST':
    website = None
    url = request.form['website']
    with urllib.request.urlopen(url) as response:
      website = response.read()
    flag = request.form.get('options')
    cloze = clozer(BeautifulSoup(website, 'html.parser').find_all('p'), flag)
    return render_template('index.html',cloze=cloze,options=options,website=url)
  else:
    return render_template('index.html')

def clozer(text, flag):
  clean_text = []
  for i in text:
      if i.string is not None:
          clean_text.append(i.string)
  text_pos = []
  for i in clean_text:
      if i is not None:
          text_pos.append(pos_tag(word_tokenize(i)))
  clean_string = []
  for i in text_pos:
      for j in i:
          if i.index(j)%5 == 0 and (flag == None or flag == "ALL"):
              clean_string.append("_____ ("+j[1]+")")
          elif j[1] == flag:
              clean_string.append("_____")
          else:
              clean_string.append(j[0])
  return " ".join(clean_string)
