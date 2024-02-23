#Chat Bot V3
'''
Natural Language Understanding
- Looks for keywords - Words that indicate intent of user. What are they requesting?
- Understands Intent - What is the user asking about? What are they asking for?
- Matches Intent and Supporting Words to Potential Responses
- Provides response - Matching the intent and requested information to find an answer. 
'''
import string
import nltk
from nltk import word_tokenize, pos_tag
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
nltk.download('punkt')
nltk.download('wordnet') 
import json
import random

from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def root():
    userMSG = request.args.get('userMSG', 'Hello')
    response = DisasterChatbot.init(userMSG)
    return json.dumps({"response": response})


class DisasterChatbot:
    #Function: Get Data from Files
    def getData(filename):
        with open(filename, 'r') as file:
            data = json.load(file)
        return data

    #Function: Part-Of-Speech Tagging
    def POS_tagging(sentence):
        tokens = word_tokenize(sentence)
    
        pos_tags = pos_tag(tokens)

        nouns = []
        adjectives = []

        for word, pos in pos_tags:
            if pos.startswith('N'):
                nouns.append(word)
                adjectives.append(word)
            elif pos.startswith('J'): 
                adjectives.append(word)
        
        return nouns, adjectives

    #Function: Match keywords to user intent
    def matchNounsToIntent(intents,nouns):
        maxMatchPattern = None
        maxMatchCount = None
        for intent in intents:
            curCount = 0
            pattern = intent["patterns"]
            for n in nouns:
                if n in pattern:
                    curCount += 1
            if maxMatchCount == None or curCount > maxMatchCount:
                maxMatchCount = curCount
                maxMatchPattern = intent["name"]

        if maxMatchPattern == None:
            return "Sorry, could you try rephrasing or rewording that?"
        return maxMatchPattern
    
    #Function: Match Support Nouns to Information Type
    def matchDescriptions(infoTypes,supports):
        maxMatchPattern = None
        maxMatchCount = None
        for curType in infoTypes:
            curCount = 0
            pattern = curType
            for a in supports:
                if a in infoTypes[pattern]:
                    curCount += 1
            if maxMatchCount == None or curCount > maxMatchCount:
                maxMatchCount = curCount
                if curType == "safety_tips_patterns":
                    maxMatchPattern = "safety_tips"
                else:
                    maxMatchPattern = "general_info"

        if maxMatchPattern == None:
            return "No Descriptions Found"
        return maxMatchPattern
    #Function: Find Appropriate Response
    def getResponse(userMSG,intents,descriptions):
        userMSG = DisasterChatbot.tokenize_stopwords(userMSG)
        pos = 0
        lemmatizer = WordNetLemmatizer()
        for i in userMSG:
            userMSG[pos] = userMSG[pos].lower()
            userMSG[pos] = lemmatizer.lemmatize(userMSG[pos])
            pos += 1
        
        stringFormMSG = ""
        for i in userMSG:
            stringFormMSG += i
            stringFormMSG += " "
        stringFormMSG = stringFormMSG.strip()
        #nouns,adjectives = DisasterChatbot.POS_tagging(stringFormMSG)

        foundIntent = DisasterChatbot.matchNounsToIntent(intents,userMSG)
        #foundDescription = DisasterChatbot.matchDescriptions(descriptions,adjectives)
        
        if foundIntent == "Sorry, could you try rephrasing or rewording that?":
            return foundIntent
        
        if foundIntent == "greeting" or foundIntent == "farewell":
            for intent in intents:
                if intent["name"] == foundIntent:
                    responses = intent["responses"]
                    break
            chosen = random.randint(0,len(responses)-1)
            return responses[chosen]

        

        foundInfoType = DisasterChatbot.matchDescriptions(descriptions,userMSG)
        if foundInfoType == "No Descriptions Found":
            foundInfoType = "general_info"
        
        for intent in intents:
            if intent["name"] == foundIntent:
                responses = intent["responses"]
                for category in responses:
                    if category["category"] == foundInfoType:
                        toReturnResponses = category["content"]
                        res = []
                        chosen = random.randint(0,len(toReturnResponses)-1)
                        res.append(toReturnResponses[chosen])
                        del(toReturnResponses[chosen])
                        chosen = random.randint(0,len(toReturnResponses)-1)
                        res.append(toReturnResponses[chosen])
                        del(toReturnResponses[chosen])
                        chosen = random.randint(0,len(toReturnResponses)-1)
                        res.append(toReturnResponses[chosen])
                        del(toReturnResponses[chosen])
                        break
        finalResponse = "\n"
        for i in res:
            finalResponse += i+"\n"
        return finalResponse

        
        


    
        
    #Function: Tokenize User Message and Remove Stop Words
    def tokenize_stopwords(message):
        message = message.translate(str.maketrans('', '', string.punctuation))
        message = message.split()

        pos = 0
        stop_words = DisasterChatbot.getStopWords()

        while pos < len(message):
            if len(message) == 0 or pos>= len(message):break
            if message[pos] in stop_words:
                del(message[pos])
            else:
                pos += 1
        return message
            

    #Function: Read Stop Words from File
    def getStopWords():
        r = open("stop_words","r")
        stop_words = set()
        while len(stop_words) < 162:
            word = r.readline()
            word = word.strip()
            stop_words.add(word)
        return stop_words


    #Function: main
    def init(userMSG):
        print("Starting Conversation:")
        knowledge = DisasterChatbot.getData("SustainabilityBotProcessingData.json")
        intents = knowledge["intents"]
        description = knowledge["info_type"]

        userMSG = userMSG.strip()

        return DisasterChatbot.getResponse(userMSG,intents,description)
