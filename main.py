from flask import (Flask, redirect, render_template, request,send_from_directory, url_for)
from openai import AzureOpenAI
import azure.cognitiveservices.speech as speechsdk
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
SYSmsg={"CourseOutline":"You are an highly helpful assistant who will be given a prompt and has to extract the highly relevant topic of the prompt then has to return questions on which material has to be gathered for understanding of that topic and so that material can be taught to an academic class as well. The 1st question must be basic with the following questions having ascending depth of material required and complexity according to the desired goal and prior knowledge of user and keywords pointing to the relevant material provided in prompt. YOU WILL ONLY RETURN QUESTIONS, NOTHING MORE AND NOTHING LESS AND if information is missing YOU WILL RESPOND \"UNSUFFICENT INFO\"","Teacher":"You are a highly skilled and knowledgeable teacher in the given topic of the prompt and are required to give a lecture on the given question and also act as if drawing on a magical board by denoting it with {} parentheses and must also explain the drawing for user understanding and are also required to ask questions and give them homework for practice. You have to give a lecture of exactly 4020 words. YOU MUST SPEAK AT LEAST 4020 WORDS, NOT ANY MORE AND NOT ANY LESS.","QNA":"You are highly helpful and understanding and intelligent academic teacher. You were giving a lecture on a specific matter when a student asked you a question. YOU MUST GIVE A DETAILED AND ACCURATE ANSWER TO THAT QUESTION WHILST ALSO REMAINING RELEVANT TO THE TOPIC OF THE LECTURE.You will answer on basis of topic of lecture which will be provided in prompt and must take into account before answering. YOU MUST IN ALL CASES END YOUR PROMPT IN SUCH A WAY THAT YOU CAN CONTINUE YOUR LECTURE LIKE \"So moving on,\" "}
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
@app.route("/session/<topic>",methods =["GET", "POST"])
def session(topic):
    if request.method=="POST":
        question=request.form.get("phraseDiv")
        print(question)
        conversation=[{"role": "system", "content":SYSmsg["QNA"]},{"role": "user", "content":f"User's topic is {topic} and Question is {question}. Keeping all this in view please generate answer relevant to the lecture whilst being detailed and accurate and YOU MUST END WITH \"So moving on, As I was saying\""}]
        response = client.chat.completions.create(model="test1", messages=conversation)
        print(response.choices[0].message.content)
    conversation=[{"role": "system", "content":SYSmsg["Teacher"]},{"role": "user", "content":topic+" Explain in great detail and be relevant"}]
    #response = client.chat.completions.create(model="test1", messages=conversation)
#    speech_synthesis_result=speech_synthesizer.speak_text_async("Hello I love you,""""response.choices[0].message.content""").get()
    return render_template("session.html",lecture="The opened package of potato chips held the answer to the mystery. Both detectives looked at it but failed to realize it was the key to solve the crime. They passed by it assuming it was random trash ensuring that the case would never be solved.")
if __name__=="__main__":
    app.run()
