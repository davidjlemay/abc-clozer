import urllib, json,redis
from nltk import word_tokenize, pos_tag
from flask import Flask, request, render_template, session
from flask_session import Session
from markupsafe import Markup, escape
from bs4 import BeautifulSoup

app = Flask(__name__)
app.config['DEBUG'] = True

SESSION_TYPE = 'redis'
SESSION_PERMANENT = False
SESSION_REDIS = redis.Redis(host='https://fierce-earth-75583.herokuapp.com/', port=6379, db=0)
app.config.from_object(__name__)

app.secret_key = b'watermelon'

Session(app)
"""
session['url'] = ""
session['cloze_html'] = {}
session['cloze_txt'] = {}
session['answers'] = []
session['true_values'] = []
"""
options = json.load(open("static/pos.json", "r"))

@app.route('/', methods=['GET', 'POST'])
def index():
  if request.method == 'POST':
    website = None
    session['url'] = request.form['website'].strip()
    with urllib.request.urlopen(session['url']) as response:
      website = response.read()
    session['choices'] = request.form.get('options')
    pos_text = clozer_pos(clean_text(BeautifulSoup(website, 'html.parser').find_all('p')))
    session['cloze_txt'] = clozer_txt(pos_text, session['choices'])
    session['cloze_html'] = clozer_html(pos_text, session['choices'])
    return render_template('index.html', cloze_txt=session['cloze_txt'],cloze_html=session['cloze_html'],options=options,website=session['url'])
  else:
    return render_template('index.html', options=options)

@app.route('/score', methods=['GET','POST'])
def score():
  session['answers'] = request.form.getlist('answer')
  scores = list(zip(session['answers'],session['true_values']))
  session['score'] = [ 1 if x[0] == x[1] else 0 for x in scores]
  correct = sum(session['score'])
  total = len(session['true_values'])
  session['answers'] = []
  score = f"{correct} correct answers out of a total of {total} for a score of {int(correct/total*100)} %"
  return render_template('index.html', cloze_txt=session['cloze_txt'],cloze_html=session['cloze_html'],options=options,website=session['url'], score=score)

#Extract string from BS4 list
def clean_text(text):
  clean_text = []
  for i in text:
      if i.string is not None:
          clean_text.append(i.string)
  return clean_text

#Tag pos in cleaned text
def clozer_pos(text):
  text_pos = []
  for i in text:
      if i is not None:
          text_pos.append(pos_tag(word_tokenize(i)))
  return text_pos

#Return text_pos formatted matching flag
def clozer_txt(text, flag):
  clean_string = []
  word_list = []
  for i in text:
      for j in i:
          if i.index(j)%5 == 0 and (flag == None or flag == "ALL"):
              clean_string.append("_____ ("+j[1]+")")
              word_list.append(j[0])
          elif j[1] == flag:
              clean_string.append("_____")
              word_list.append(j[0])
          else:
              clean_string.append(j[0])
  return {"text": " ".join(clean_string), "words": ", ".join(word_list)}

#Return html_pos formatted matching flag with true values for scoring
def clozer_html(text, flag):
  clean_string = []
  word_list = []
  for i in text:
      for j in i:
          if i.index(j)%5 == 0 and (flag == None or flag == "ALL"):
            clean_string.append("<input type='text' id='"+j[0]+"' name='answer' size='10'><label for='answer'>("+j[1]+")</label>")
            word_list.append(j[0])
          elif j[1] == flag:
            clean_string.append("<input type='text' id='"+j[0]+"' name='answer' size='10'>")
            word_list.append(j[0])
          else:
            clean_string.append(j[0])
  session['true_values'] = word_list
  return {"text": Markup(" ".join(clean_string)), "words": ", ".join(sorted(word_list))}

if __name__ == '__main__':
  app.run(threaded=True, port=5000)
