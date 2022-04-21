from spacy import load
from numerizer import numerize
import re
import pandas as pd
import fasttext as ft

# Ignore fastText warning
ft.FastText.eprint = lambda x: None

# Load the pretrained models
# Language detection models
ft_model = ft.load_model("./res/lid.176.bin")

# NLP languages from spicy
english_model = 'en_core_web_sm'
spanish_model = 'es_core_news_sm'
french_model = 'fr_core_news_sm'


# Currency code list
def check_currency(msg):
    # read csv with currency info
    col_list = ['Entity', 'Currency', 'AlphabeticCode', 'NumericCode', 'MinorUnit', 'WithdrawalDate']
    df = pd.read_csv('./res/codes-all.csv', usecols=col_list)

    # search code in msg
    codes = df['AlphabeticCode'].tolist()               # list of currency codes
    codes = filter(lambda i: (type(i) is str), codes)   # remove no string elements
    codes = list(dict.fromkeys(codes))                  # remove duplicate items
    codes = (map(lambda x: x.lower(), codes))           # make lowercase
    matched_codes = [i for i in codes if i in msg.split()]

    return matched_codes


def nearest_word(msg, wb, w1, w2):
    msg_list = msg.split()
    pb = msg_list.index(wb)
    p1 = msg_list.index(w1)
    p2 = msg_list.index(w2)

    if abs(p1 - pb) < abs(p2 - pb):
        return w1, w2
    else:
        return w2, w1


def fasttext_language_predict(text, model=ft_model):
    text = text.replace('\n', " ")
    prediction = model.predict([text])[0][0][0]
    return prediction


def process_msg(msg):
    # Fist filter: language (es, en, fr)
    lang = fasttext_language_predict(msg)

    # English lang allows the use of numerize package
    if lang == '__label__en':
        msg = numerize(msg)

    # Second filter: msg with or without amount
    amount_str = re.findall('\d*\.?\d+', msg)
    if len(amount_str) == 1:
        amount = float(amount_str[0])
    elif len(amount_str) > 1:
        amount = -1     # ERROR: unique amount needed
    else:
        amount = 0      # No amount request

    # Get codes involved in conversion
    codes = check_currency(msg)
    if len(codes) != 2:
        return lang, amount, None, None

    # Get base and units
    if amount > 0:
        base_unit, target_unit = nearest_word(msg, amount_str[0], codes[0], codes[1])
    else:
        base_unit = codes[0]
        target_unit = codes[1]

    return lang, amount, base_unit.upper(), target_unit.upper()


"""
nlp = load(english_model)
doc = nlp('dos mil mi mama me ama')
print(doc)
str_dig = numerize(str(doc))
print(str_dig)
print(re.findall('\d*\.?\d+', str_dig))
"""
msg_eg = "Conversor de divisas COP a EUR".lower()
print(process_msg(msg_eg))

