from flask import Flask, redirect, render_template, request,send_from_directory, url_for, jsonify
from openai import AzureOpenAI
import base64
import azure.cognitiveservices.speech as speechsdk
import re
import requests
import urllib.parse
import random
import concurrent.futures
import numpy as np
from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from azure.cognitiveservices.vision.customvision.training.models import ImageFileCreateBatch, ImageFileCreateEntry, Region
from msrest.authentication import ApiKeyCredentials
topic=""
keywords=""
priork=""
goal=""
classnum=""
client = AzureOpenAI(
  api_key = "84b60c0de34e4c2ebe578a598e687fec",  
  api_version = "2023-05-15",
  azure_endpoint = "https://cogniteach-openai.openai.azure.com/openai/deployments/test1/chat/completions?api-version=2023-07-01-preview")
prediction_credentials = ApiKeyCredentials(in_headers={"Prediction-key": "acc584d19dbd4bfd81d133deb2488d68"})
predictor = CustomVisionPredictionClient("https://cogniteachemotionrecognition-prediction.cognitiveservices.azure.com/", prediction_credentials)
app=Flask(__name__)
def searchParse(x,imageType,count):
    subscription_key = "0a8a7303d7f74a9aba8ec7f46321ed86"
    endpoint = "https://api.bing.microsoft.com/v7.0/images/search"
    mkt = 'en-US'
    params = { 'q': x, 'mkt': mkt,'count':count,'imageType': urllib.parse.quote(imageType) }
    headers = { 'Ocp-Apim-Subscription-Key': subscription_key }
    # Call the API
    try:
        response = requests.get(endpoint, headers=headers, params=params)
        response.raise_for_status()
        jsona=response.json()
        clipartURLs=[]
        for i in jsona['value']:
            clipartURLs.append(i['contentUrl'])
        return clipartURLs
    except Exception as ex:
        raise ex
def is_image_url(url):
    try:
        response = requests.head(url, timeout=5)  # Set a timeout to prevent long waits
        content_type = response.headers.get('content-type')

        if content_type is not None and content_type.startswith('image'):
            return True
        else:
            return False
    except requests.RequestException:
        return False
def check_image_urls(urls):
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:  # Adjust max_workers as needed
        results = list(executor.map(is_image_url, urls))
def outpics(it):
    output=[]
    result_clipart = searchParse(it, imageType='Clipart',count=6)
    result_photo = searchParse(it, imageType='Photo',count=6)
    result_line = searchParse(it, imageType='Line',count=6)
    for i in result_clipart:
            if not check_image_urls(i):
                result_clipart.remove(i)
    for i in result_photo:
            if not check_image_urls(i):
                result_photo.remove(i)
    for i in result_line:
            if not check_image_urls(i):
                result_line.remove(i)
    final=[]
    final.append(random.choice(result_clipart))
    final.append(random.choice(result_photo))
    final.append(random.choice(result_line))
    output.append(final)
    return output
def extract_and_replace(paragraph):
    text_between_hyphen = re.findall(r'\{-([^{}]*)-\}', paragraph)
    text_between_slash = re.findall(r'\{\/([^{}]*)\/\}', paragraph)

    replaced_paragraph = re.sub(r'\{-([^{}]*)-\}', '&', paragraph)
    replaced_paragraph = re.sub(r'\{\/([^{}]*)\/\}', '@', replaced_paragraph)

    return text_between_hyphen, text_between_slash, replaced_paragraph
def is_even_position(element, lst):
    if element in lst:
        idx = lst.index(element)
        return idx % 2 == 0
SYSmsg={"CourseOutline":"You are an highly helpful assistant who will be given a prompt and has to extract the highly relevant topic of the prompt then has to return questions on which material has to be gathered for understanding of that topic and so that material can be taught to an academic class as well. The 1st question must be basic with the following questions having ascending depth of material required and complexity according to the desired goal and prior knowledge of user and keywords pointing to the relevant material provided in prompt. YOU WILL ONLY RETURN QUESTIONS, NOTHING MORE AND NOTHING LESS whilst keeping in mind of all the details given in prompt ","Teacher":"You are a highly skilled and knowledgeable teacher in the given topic of the prompt and are required to give a interactive lecture on the given question and also act as if drawing and writing on a magical board by denoting it with {--} for image or drawing and {--} for text and must use it properly at least 25 Times, YOU WILL WRITE ALL NUMBERS,KEYWORDS AND CALCULATIONS ON THE BOARD and must also explain the drawing for user understanding and are also required to ask questions and give them homework for practice. You will give the lecture in small parts in which you will talk with the user and the user will respond to you and then you will continue, it will be like a conversation. In each response you must use the board to show a image and in the end of each response you must ask user a content lecture related question which the user will answer and you shall link the next content from there. You will also sometimes joke with the user regarding the topic and excluding jokes that need 2 people to interact to be understood. You will also give user tips and tricks like but not limited to abbreviations to help memorize the information faster and more easily. Your combined responses must be total 4020 words.You must carry on the conversation always eg. if user asks query, you respond to it whilst being relevant to lecture and at the end come back to the lecture topic and when asking a question try to make it so a normal person can see this as a question. Each of your response musnt be too long but not too short also. You have to give a lecture of exactly 4020 words. YOU MUST SPEAK AT LEAST 4020 WORDS, NOT ANY MORE AND NOT ANY LESS. YOU MUST GIVE 25 responses after which you will quiz the user and grade him on his performance before exactly saying [LECTURE ENDED].If you are given the user's info and instructions and in the end a pair square brackets(\"[]\") you must start the educational conversation regarding the topic and YOU MUST REMAIN RELEVANT TO TOPIC IN ALL CASES whenever you need to end lecture you will simply return \'[LECTURE ENDED]\. you must have a question at the end of each of your response so the user can respond after properly addressing all queries, assigning work, giving tips and tricks to better memorize and doing educational related fun activities with the user and properly concluding the lecture, you must also give user classwork like asking them to write down answers to questions you give them or asking them to write down points you will give so they can come back to it later","QNA":"You are highly helpful and understanding and intelligent academic teacher. You were giving a lecture on a specific matter when a student asked you a question. YOU MUST GIVE A DETAILED AND ACCURATE ANSWER TO THAT QUESTION WHILST ALSO REMAINING RELEVANT TO THE TOPIC OF THE LECTURE.You will answer on basis of topic of lecture which will be provided in prompt and must take into account before answering. YOU MUST IN ALL CASES END YOUR PROMPT IN SUCH A WAY THAT YOU CAN CONTINUE YOUR LECTURE LIKE \"So moving on,\" ","Smalltalk":"Your name is Teresa .You will be given an predicted emotion of a person and their name and their mental state and their age so must talk with them and ask them questions etc. and try to help them if they are feeling anything negative and help them in personal growth and grooming just like a very close teacher. If you are given the user's info and in the end a pair square brackets(\"[]\") you must start a conversation by introducing yourself as a teacher for todays lesson but do not mention the subject you will be teaching and must talk and interact with the user to foster emotional growth like a therapist and also ask about their day, why are they feeling the emotion that can be seen on their face etc. After precisely 5 messages by you, you shall say something like \'Shall we start today's lecture?\' without explicitly or implicitly stating topic of lecture to which the user will respond positively indicating to start lecture if the user doesnt then you shall carry on the conversation for another 5 messages before trying to make user start the lecture again. After the user responds positively to starting lecture YOU SHALL RETURN A FINAL MESSAGE PRECISELY SAYING \"[LECTURE STARTED]\" AND ABSOLUTELY NOTHING ELSE"}


@app.route("/")
def home():
    return redirect(url_for('signup'))

@app.route('/get_url', methods=['POST'])
def get_url():
    element = request.form['element']  # Get the 'element' variable from the request
    # Use the 'element' variable in the url_for function
    url = url_for('session', topic=element, _external=True)
    return jsonify({'url': url})
@app.route("/setup",methods =["GET", "POST"])
def ss_setup():
    if request.method == "POST":
       topic = request.form.get("topic")
       keywords = request.form.get("keywords")
       priork = request.form.get("prior")
       goal = request.form.get("goal")
       classnum = request.form.get("classnum")
       density = request.form.get("density")
       conversation=[{"role": "system", "content":SYSmsg["CourseOutline"]},{"role": "user", "content":f"User's topic is {topic} and goal is {goal} and important keywords are {keywords} prior knowledge is {priork} and number of questions to be generated are {classnum} and amount of syllabus to be covered on a scale of 1-100 is {density}/100. Keeping all this in view please generate Q on which material must be gathered to be taught to a class"}]
       response = client.chat.completions.create(model="test1", messages=conversation)
       return redirect(url_for('outline',info=response.choices[0].message.content,topica=topic))
    return render_template("ss_setup.html")


@app.route("/outline/<info>/<topica>")
def outline(info,topica):
    questions = info.split("?")
    return render_template('outline.html', qs=questions,topica=topica)

@app.route('/capture', methods=['POST'])
def capture():
    image_data = request.form['image_data']
    lmao=['Anger','Disgust','Contempt','Neutral','Neutral','Neutral','Neutral','Contempt','Contempt','Contempt','Happiness','Happiness','Happiness','Happiness']
    # Send the image to the backend (replace 'YOUR_BACKEND_ENDPOINT' with the actual endpoint)
    return jsonify({"status": "success","server_response": random.choice(lmao)})
@app.route('/smalltalk', methods=['POST'])
def smalltalk():
    emotion=request.form['mood']
    name=request.form['name']
    age=request.form['age']
    state=request.form['mentalstate']
    history=request.form['history']
    print(f"hello ! {history}")
    conversation=[{"role":"system", "content":SYSmsg["Smalltalk"]},{"role":"user","content":f"user's name is{name} and age is{age} and emotion is {emotion} and mental state is {state} []"}]
    if history == "":
        response = client.chat.completions.create(model="test1", messages=conversation)
        yessir=response.choices[0].message.content
        return jsonify(result=yessir)
    else:
        responses = history.split("|")
        for i in responses:
            if is_even_position(i,responses):
                conversation.append({"role":"assistant","content":i})
            else:
                conversation.append({"role":"user","content":i})
                
        response = client.chat.completions.create(model="test1", messages=conversation)
        yessir=response.choices[0].message.content
        return jsonify(result=yessir)

@app.route("/lecture",methods=['POST'])
def lecture():
    history=request.form['history']
    name=request.form['name']
    age=request.form['age']
    qualifications=request.form['academic']
    lang_rating=request.form['lang_rating']
    concept_rating=request.form['concept_rating']
    topic=request.form['topic']
    classwork=''
    conversation=[{"role":"system", "content":SYSmsg["Teacher"]},{"role":"user","content":f"Topic Question is {topic} and user's name is{name} and age is{age} and academic qualifications are {qualifications} and language understanding is {lang_rating}/10 and conceptual grasp ability is {concept_rating}/10. Please give a response that starts the conversation given that the user and you have participated in small talk and give responses accordingly with text between "+"{- and -} to denote writing on board e.g {-this is text to be written on board-} and you must also display images which is denoted by placing the text describing the image between {- and -} to denote displaying of images eg. {-image of a boat-}. Please use this feature at end of each response and only you can use the board and give a lecture to user in form of a conversation . and give end each response with a respondable question []"}]
    if history == "":
        response = client.chat.completions.create(model="test1", messages=conversation)
        writings,drawings,lecture_text=extract_and_replace(response.choices[0].message.content)
        drawings_parsed=outpics(writings)
        print(drawings_parsed)
        return jsonify(result=lecture_text,images=drawings_parsed)
    else:
        responses = history.split("|")
        for i in responses:
            if is_even_position(i,responses):
                conversation.append({"role":"assistant","content":i})
            else:
                conversation.append({"role":"user","content":i})
        response = client.chat.completions.create(model="test1", messages=conversation)
        writings,drawings,lecture_text=extract_and_replace(response.choices[0].message.content)
        convo=[{"role":"system","content":"YOU WILL BE GIVEN A TEXT AND MUST RETURN WORDS OR IMPORTANT CALCULATIONS OR EQUATIONS OR KEYWORDS THAT CAN BE WRITTEN AND YOU MUST RETURN ABSOLUTELY NOTHING ELSE"},{"role":"user","content":lecture_text}]
        board_writings=client.chat.completions.create(model="test1", messages=convo)
        convo2=[{"role":"system","content":"YOU WILL BE GIVEN A TEXT AND MUST RETURN EXACTLY 4 WORDS THAT CAN BE SEARCHED UP AND SO A IMAGE RELATED TO THESE 4 WORDS CAN BE DISPLAYED AND YOU MUST RETURN ABSOLUTELY NOTHING ELSE"},{"role":"user","content":lecture_text}]
        board_images=client.chat.completions.create(model="test1", messages=convo2)
        drawings_parsed=outpics(board_images.choices[0].message.content)
        print(drawings_parsed)
        return jsonify(result=lecture_text,images=drawings_parsed,board_text=board_writings.choices[0].message.content)
                

@app.route("/askgpt",methods=['POST'])
def askgpt():
        ahaha = request.form['q']
        age=request.form['age']
        qualifications=request.form['academic']
        lang_rating=request.form['lang_rating']
        concept_rating=request.form['concept_rating']
        topic=request.form['topic']
        conversation=[{"role": "system", "content":SYSmsg["QNA"]},{"role": "user", "content":f"User's topic is {topic} and Question is {ahaha} keeping in mind that users qualifications are {qualifications} and language understanding is {lang_rating}/10 and concept grasping ability is {concept_rating}/10 and age is {age}"}]
        response = client.chat.completions.create(model="test1", messages=conversation)
        yessir=response.choices[0].message.content
        return jsonify(result=yessir)


@app.route('/signup')
def signup():
    return render_template('signup.html')
@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")
@app.route('/antipro')
def antipro():
    return render_template("antipro.html")
@app.route("/session/<topic>",methods =["GET", "POST"])
def session(topic):
    return render_template("session.html",topic=topic)




if __name__=="__main__":
    app.run(debug=True)
