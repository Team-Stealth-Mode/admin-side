
from nltk.sentiment import SentimentIntensityAnalyzer
import firebase_admin
from firebase_admin import credentials, firestore
import nltk

nltk.download('vader_lexicon')

data = {'tilak.dave22': {'count': 28,
                         'happy': 8,
                         'neutral': 12,
                         'angry': 0,
                         'sad': 0,
                         'fearful': 0,
                         'disgusted': 0,
                         'surprised': 0,
                         'sentences': ['Want to say?', 'Want to say?', 'Want to say?', 'Want to say?', 'Want to say?', 'Want to say?', 'Want to say?', 'So guys this is still the way and my face is getting detected and all the data is.', 'So guys this is still the way and my face is getting detected and all the data is.', 'So guys this is still the way and my face is getting detected and all the data is.', 'Console.', 'Console.', 'I think that I should speak very less because our.', 'I think that I should speak very less because our.', 'I think that I should speak very less because our.', 'I think that I should speak very less because our.', 'I think that I should speak very less because our.', 'I think that I should speak very less because our.', 'I think that I should speak very less because our.', 'I think that I should speak very less because our.', 'I think that I should speak very less because our.', 'I think that I should speak very less because our.', "They really really poor that it cannot understand fast sentences. Now because Siddesh is looking at the console logs I'm not able to see.", "They really really poor that it cannot understand fast sentences. Now because Siddesh is looking at the console logs I'm not able to see.", "They really really poor that it cannot understand fast sentences. Now because Siddesh is looking at the console logs I'm not able to see.", "They really really poor that it cannot understand fast sentences. Now because Siddesh is looking at the console logs I'm not able to see.", "Too long I have to talk, but I'll be keep talking until and unless I.", "Too long I have to talk, but I'll be keep talking until and unless I."]},

        'akash.deshmukh22': {'count': 0,
                             'happy': 0,
                             'neutral': 0,
                             'angry': 0,
                             'sad': 0,
                             'fearful': 0, 'disgusted': 0, 'surprised': 0, 'sentences': []}, 'siddhesh.shinde22': {'count': 0, 'happy': 0, 'neutral': 0, 'angry': 0, 'sad': 0, 'fearful': 0, 'disgusted': 0, 'surprised': 0, 'sentences': []}, 'soham.dixit22': {'count': 0, 'happy': 0, 'neutral': 0, 'angry': 0, 'sad': 0, 'fearful': 0, 'disgusted': 0, 'surprised': 0, 'sentences': []}}


    
        

cred = credentials.Certificate("./key.json")
firebase_admin.initialize_app(cred)

nltk.download('vader_lexicon')


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
print(type(score["pos"]))
num = 0;
if score["pos"] > 0.5:
    num = num + 5
if score["pos"] > 0.8:
    num = num + 10
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
doc = collection.where('email', '==', f'{username}@vit.edu');
fidoc = db.collection('users').document(doc.get()[0].to_dict()['uid']).collection('financial').document('4InrqaLeE9NamW8qg5Xi')
print(fidoc.get().to_dict())

calculateScore(fidoc.get().to_dict(), doc)
# scs = doc['social_credit_score']
print(doc.get()[0].to_dict()['social_credit_score'] + num)
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
doc.get()[0].reference.update(response)


