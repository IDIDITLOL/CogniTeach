from flask import Flask, redirect, render_template, request,send_from_directory, url_for, jsonify
from openai import AzureOpenAI
import azure.cognitiveservices.speech as speechsdk
import re
import requests
import urllib.parse
import random
import concurrent.futures
topic=""
keywords=""
priork=""
goal=""
classnum=""
client = AzureOpenAI(
  api_key = "84b60c0de34e4c2ebe578a598e687fec",  
  api_version = "2023-05-15",
  azure_endpoint = "https://cogniteach-openai.openai.azure.com/openai/deployments/test1/chat/completions?api-version=2023-07-01-preview")
#speech_config = speechsdk.SpeechConfig(subscription="8f0b068bc2f246509f2b26884bf739ee",region="eastus")
#audio_config = speechsdk.audio.AudioOutputConfig(filename="static/file.wav")
#speech_config.speech_synthesis_voice_name='en-US-EmmaNeural'
#speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
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
def outpics(list1):
    output=[]
    for i in list1:
        result_clipart = searchParse(i, imageType='Clipart',count=6)
        result_photo = searchParse(i, imageType='Photo',count=6)
        result_line = searchParse(i, imageType='Line',count=6)
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
def extract_and_remove_brackets(text):
    pattern_slash = r'\{/(?P<slash>.*?)\}'
    pattern_dash = r'\{-(?P<dash>.*?)-\}'
    matches_slash = re.findall(pattern_slash, text)
    matches_dash = re.findall(pattern_dash, text)
    cleaned_text = re.sub(pattern_slash, 'umm', text)
    cleaned_text = re.sub(pattern_dash, 'hmm', cleaned_text)
    return matches_slash, matches_dash, cleaned_text

SYSmsg={"CourseOutline":"You are an highly helpful assistant who will be given a prompt and has to extract the highly relevant topic of the prompt then has to return questions on which material has to be gathered for understanding of that topic and so that material can be taught to an academic class as well. The 1st question must be basic with the following questions having ascending depth of material required and complexity according to the desired goal and prior knowledge of user and keywords pointing to the relevant material provided in prompt. YOU WILL ONLY RETURN QUESTIONS, NOTHING MORE AND NOTHING LESS AND if information is missing YOU WILL RESPOND \"UNSUFFICENT INFO\"","Teacher":"You are a highly skilled and knowledgeable teacher in the given topic of the prompt and are required to give a lecture on the given question and also act as if drawing and writing on a magical board by denoting it with {//} for image or drawing and {--} for text and must use it properly at least 25 Times, YOU WILL WRITE ALL NUMBERS,KEYWORDS AND CALCULATIONS ON THE BOARD and must also explain the drawing for user understanding and are also required to ask questions and give them homework for practice. You have to give a lecture of exactly 4020 words. YOU MUST SPEAK AT LEAST 4020 WORDS, NOT ANY MORE AND NOT ANY LESS.","QNA":"You are highly helpful and understanding and intelligent academic teacher. You were giving a lecture on a specific matter when a student asked you a question. YOU MUST GIVE A DETAILED AND ACCURATE ANSWER TO THAT QUESTION WHILST ALSO REMAINING RELEVANT TO THE TOPIC OF THE LECTURE.You will answer on basis of topic of lecture which will be provided in prompt and must take into account before answering. YOU MUST IN ALL CASES END YOUR PROMPT IN SUCH A WAY THAT YOU CAN CONTINUE YOUR LECTURE LIKE \"So moving on,\" "}


@app.route("/")
def home():
    return render_template("imalive.html")
@app.route("/setup",methods =["GET", "POST"])
def ss_setup():
    if request.method == "POST":
       topic = request.form.get("topic")
       keywords = request.form.get("keywords")
       priork = request.form.get("prior")
       goal = request.form.get("goal")
       classnum = request.form.get("classnum")
       conversation=[{"role": "system", "content":SYSmsg["CourseOutline"]},{"role": "user", "content":f"User's topic is {topic} and goal is {goal} and important keywords are {keywords} prior knowledge is {priork} and number of questions to be generated are {classnum}. Keeping all this in view please generate Q on which material must be gathered to be taught to a class"}]
       response = client.chat.completions.create(model="test1", messages=conversation)
       return redirect(url_for('outline',info=response.choices[0].message.content))
    return render_template("ss_setup.html")


@app.route("/outline/<info>")
def outline(info):
    questions = info.split("?")
    return render_template('outline.html', qs=questions)

@app.route("/askgpt")
def askgpt():
    try:
        ahaha = request.args.get('phraseDiv')
        conversation=[{"role": "system", "content":SYSmsg["QNA"]},{"role": "user", "content":f"User's topic is {topic} and Question is {ahaha}. Keeping all this in view please generate answer relevant to the lecture whilst accurately answering question and YOU MUST END WITH \"So moving on, As I was saying\""}]
        response = client.chat.completions.create(model="test1", messages=conversation)
        yessir=response.choices[0].message.content
        return jsonify(result=yessir)
    except Exception as e:
        print("ERROR:", str(e))

@app.route("/session/<topic>",methods =["GET", "POST"])
def session(topic):
    if request.method=="POST":
        print("lol")

    conversation=[{"role": "system", "content":SYSmsg["Teacher"]},{"role": "user", "content":topic+" Explain in great detail and be relevant"}]
    #response = client.chat.completions.create(model="test1", messages=conversation)
    response="I recollect that my first exploit in {-exploit-} squirrel-shooting was in a grove {-grove-} of tall walnut-trees {/tall walnut trees/} that shades one side of the valley. I had wandered into it at noontime, when all nature is peculiarly quiet {-peculiarly-} , and was startled by the roar of my own gun {/gun/} , as it broke the Sabbath stillness {-Sabbath-} around and was prolonged and reverberated by the angry echoes.If you can imagine a furry humanoid seven feet tall, with the face of an intelligent gorilla and the braincase of a man, you'll have a rough idea of what they looked like -- except for their teeth {/bigfoot mythological creature/}. The canines would have fitted better in the face of a tiger, and showed at the corners of their wide, thin-lipped mouths, giving them an expression of {/angry/} ferocity. {-ferocity-}"
#    speech_synthesis_result=speech_synthesizer.speak_text_async("Hello I love you,""""response.choices[0].message.content""").get()
    list1,list2,text=extract_and_remove_brackets(response)
    images_Board=outpics(list1)
    return render_template("session.html",lecture=text,board_writings=list2,images=images_Board)




if __name__=="__main__":
    app.run(debug=True)
