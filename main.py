from flask import Flask, request, render_template
from flask_cors import cross_origin
from nltk.sentiment import SentimentIntensityAnalyzer
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import nltk

cred = credentials.Certificate("./key.json")
firebase_admin.initialize_app(cred)

nltk.download('vader_lexicon')

app = Flask(__name__)


@app.route('/api', methods=['POST'])
@cross_origin()
def api():
    data = request.json
    max_val = 0
    for i in data:
        if data[i]['count'] > max_val:
            max_val = data[i]['count']
            username = i

    user = data[username]
    max_val = 0
    for i in user:
        if i == 'count' or i == 'sentences':
            continue
        if user[i] > max_val:
            max_val = user[i]
            max_key = i

    user_sentences = list(set(user['sentences']))
    string = ""
    for i in user_sentences:
        string = string + i

    sia = SentimentIntensityAnalyzer()
    score = sia.polarity_scores(string)
    print(score)
    num = 0
    if score["pos"] > 0.5:
        num = num + 5
    if score["pos"] > 0.8:
        num = num - 10
    if score["neg"] > 0.5:
        num = num - 5
    if score["neu"] > 0.8:
        num = num + 2
    if max_key == "happy" or max_key == "neutral" or max_key == "surprised":
        num = num + 6
    else:
        num = num - 6
    

    db = firestore.client()  # this connects to our Firestore database
    collection = db.collection('users')  # opens 'places' collection
    doc = collection.where('email', '==', f'{username}@vit.edu')
    realtime_data = db.collection('users').document(doc.get()[0].to_dict()['uid']).collection('realtime_data')
    # create a new document in the collection
    realtime_data.add({
        'time': firestore.SERVER_TIMESTAMP,
        'user_sia': {
            "positive": score["pos"],
            "negative": score["neg"],
            "neutral": score["neu"],
        },
        "user_expresions": {
            max_key: user[max_key]
        },
    })

    
    
    # realtime_data.document().set({
    #     'time': firestore.SERVER_TIMESTAMP,
    #     'user_sia': {
    #         "positive": score["pos"],
    #         "negative": score["neg"],
    #         "neutral": score["neu"],
    #     },
    #     "user_expresions": {
    #         max_key: user[max_key]
    #     },
    # })

    # scs = doc['social_credit_score']
    print(doc.get()[0].to_dict()['social_credit_score'])
    
    # print(doc.get()[0]["financial"][0].to_dict()['a_income'])
    response = {
        "user_sia": {
            "positive": score["pos"],
            "negative": score["neg"],
            "neutral": score["neu"],
        },
        "user_expresions": {
            max_key: user[max_key]
        },
        "social_credit_score": doc.get()[0].to_dict()['social_credit_score'] + num
    }
    # if date.now().day == 1:
    #     fidoc = db.collection('users').document(doc.get()[0].to_dict()['uid']).collection('financial').document('4InrqaLeE9NamW8qg5Xi')
    #     calculateScore(fidoc.get().to_dict(), doc)
    doc.get()[0].reference.update(response)
    return response

def calculateScore(data, doc):
    num = 0
    if data["no_of_bank_acc"] == 1 or data["no_of_bank_acc"] == 2:
        num = num + 3
    if data["no_of_bank_acc"] == 3:
        num = num + 2
    if data["no_of_bank_acc"] > 3:
        num = num - 2
    if data["no_of_credit_cards"] <= 2:
        num = num + 3
    if data["no_of_credit_cards"] > 2 and data["from_due_date"] >3 and data["total_delayed_dates"] > 5:
        num = num - 3
    elif data["no_of_credit_cards"] > 2 and data["from_due_date"] >3 and data["total_delayed_dates"] < 3:
        num = num + 1
    else:
        num = num + 3
    if data["m_income"]/data["debt"] < data["no_of_loans"]:
        num = num - 2
    else:
        num = num + 2
    if data["credit_utilization_ration"] > (data["credit_limit"]*35)/100:
        num = num - 1
    else:
        num = num + 2
    if data["total_emi"] > (data["m_income"]*35)/100:
        num = num - 1
    elif data["total_emi"] > (data["m_income"]*45)/100:
        num = num - 2
    elif data["total_emi"] < (data["m_income"]*35)/100:
        num = num + 3
    finupdate = {
        "social_credit_score": doc.get()[0].to_dict()['social_credit_score'] + num
    }
    doc.get()[0].reference.update(finupdate)


@app.route('/')
def index():
    return render_template('./index.html')


if __name__ == '__main__':
    app.run()
