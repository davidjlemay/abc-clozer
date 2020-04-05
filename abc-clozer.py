import urllib, json
from nltk import word_tokenize, pos_tag
from flask import Flask, request, render_template
from markupsafe import Markup
from bs4 import BeautifulSoup

app = Flask(__name__)
app.config['DEBUG'] = True

options = json.load(open("static/pos.json", "r"))

@app.route('/', methods=['GET', 'POST'])
def index():
  if request.method == 'POST':
    website = None
    url = request.form['website']
    with urllib.request.urlopen(url) as response:
      website = response.read()
    flag = request.form.get('options')
    pos_text = clozer_pos(clean_text(BeautifulSoup(website, 'html.parser').find_all('p')))
    cloze_txt = clozer_txt(pos_text, flag)
    cloze_html = clozer_html(pos_text, flag)
    return render_template('index.html',cloze_txt=cloze_txt,cloze_html=cloze_html,options=options,website=url.strip())
  else:
    return render_template('index.html')

@app.route('/score', methods=['POST'])
def score():
  answers = request.form['answers']
  true_values = request.form['true_values']
  scores = zip(answers,true_values)
  score = [ 1 if x[0] == x[1] else 0 for x in scores]
  return render_template('index.html',cloze_txt=cloze_txt,cloze_html=cloze_html,options=options,website=url.strip(),score=score)

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
  text_body = " ".join(clean_string)
  return {"text": " ".join(clean_string), "words": ", ".join(word_list)}

#Return html_pos formatted matching flag
def clozer_html(text, flag):
  clean_string = []
  word_list = []
  for i in text:
      for j in i:
          if i.index(j)%5 == 0 and (flag == None or flag == "ALL"):
            clean_string.append("<input type='text' id='"+j[0]+"' name='"+j[0]+str(i.index(j))+"' size='10'><label for='"+j[0]+str(i.index(j))+"'>("+j[1]+")</label>")
            word_list.append(j[0])
          elif j[1] == flag:
            clean_string.append("<input type='text' id='"+j[0]+"' name='"+j[0]+str(i.index(j))+"' size='10'>")
            word_list.append(j[0])
          else:
            clean_string.append(j[0])
  return {"text": Markup(" ".join(clean_string)), "words": ", ".join(word_list)}

def score()

if __name__ == '__main__':
  app.run()
