from flask import Blueprint, Flask, render_template, request, jsonify, flash, redirect
import time
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, Chat
import os
from . import db
import secrets
import datetime
#from PIL import Image #fotoğrafları gösterirken lazım
#import openai
from openai import OpenAI

client = OpenAI(
    api_key="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"
)

views = Blueprint('views', __name__)

@views.route("/about")
@login_required
def about():
    return render_template("about.html", user=current_user)


@views.route("/", methods=['GET', 'POST'])
@login_required
def home():
    print(current_user)
    message_text = None
    chat_id = -1
    if request.method == 'POST': 
        chat_id = request.form.get('chat_id')
        print("Home chat_id:")
        print(chat_id)
    print("chat_id in home: " + str(chat_id))
    message_text = chat_id
    
    date = datetime.datetime.now()         
    chat_history = ""
    other_chats = []
    all_chats = []
    #read from max.txt to get max chat id
    max_chat_id = 0
    with open("bitirme/max.txt", "r") as file:
        max_chat_id = int(file.read())
        file.close()
    #write to max.txt to update max chat id
    with open("bitirme/max.txt", "w") as file:
        file.write(str(max_chat_id + 1))
        file.close()
    with db.engine.connect() as con:
        all_chats = con.execute("SELECT * FROM Chat WHERE user_id = " + str(current_user.id)).fetchall()
    
     
    if len(all_chats) <1:  
        other_chats.append([max_chat_id, "New Chat", "Yeni bir chat oluştur"])
        chat_history = "selam nasılsın ? Nasıl yardımcı olabilirim ? /c "
        with db.engine.connect() as con:
            con.execute("INSERT INTO Chat (id, user_id, baslik, date, kisa_aciklama, chat_history) VALUES ( "+str(max_chat_id)+", "  + str(current_user.id) + ", 'New Chat', '"+ str(date) +"', 'Yeni bir chat oluştur', '" + chat_history + "')")
        message_text = max_chat_id
    else: 
        if message_text != -1:
            #find chat history from all_chats which baslik is message_text
            print("message_text: " + message_text)
            if str(message_text) == str(0):
                print("message_text in: " + message_text)
                chat_history = "selam nasılsın ? Nasıl yardımcı olabilirim ? /c "
                other_chats.append([max_chat_id ,"New Chat", "Yeni bir chat oluştur"])
                with db.engine.connect() as con:
                    con.execute("INSERT INTO Chat (id, user_id, baslik, date, kisa_aciklama, chat_history) VALUES ( "+str(max_chat_id)+", "  + str(current_user.id) + ", 'New Chat', '"+ str(date) +"', 'Yeni bir chat oluştur', '" + chat_history + "')")
                message_text = max_chat_id
            else:
                print("message_text out: " + message_text)
                for chat in all_chats:
                    if str(chat.id) == str(message_text):
                        chat_history = chat.chat_history
                        break
            for chat in all_chats:
                other_chats.append([chat.id, chat.baslik, chat.kisa_aciklama])
        else:
            #find last chat history from all_chats which user id is current_user.id and date is max
                        
            last_chat = None
            for chat in all_chats:
                if last_chat == None:
                    last_chat = chat
                elif chat.date > last_chat.date:      
                    last_chat = chat
            if last_chat != None:
                chat_history = last_chat.chat_history
                message_text = last_chat.id
            for chat in all_chats:
                other_chats.append([chat.id, chat.baslik, chat.kisa_aciklama])                   
            
    #print("chat_history: " + chat_history)
    chat_history = chat_history.split("/c")
    #print("chat len")
    #print(len(chat_history))
    for i in range(len(chat_history)-1):
        if i % 2 == 0:
            chat_history[i] = [0, chat_history[i]]
            print(chat_history[i])
        else:
            chat_history[i] = [1, chat_history[i]]
            print(chat_history[i])
    #for i in range(len(chat_history)):
    #    print(chat_history[i])
    #change other_chats like this other_chats = [["Hava durumu", "bugünün verilerine göre hava durumu ..."],["Hava durumu", "bugünün verilerine göre hava durumu ..."],["chat 2", "asdasd asd.as.das as..."],["chat 3", "cqwdasd asda sdasd asd..."]]
    #other_chats = [["Hava durumu", "bugünün verilerine göre hava durumu ..."],["Hava durumu", "bugünün verilerine göre hava durumu ..."],["chat 2", "asdasd asd.as.das as..."],["chat 3", "cqwdasd asda sdasd asd..."]]

  
    return render_template("index.html", user=current_user, chat_id = message_text, chats = chat_history, other_chats = other_chats)


@views.route("/send_message", methods=['POST'])
@login_required
def send_message():
    message_text = request.form['message']
    chat_id = request.form['chat_id']
   
    prompt = message_text
    chat_completion = client.chat.completions.create(
        messages = [
            {
                "role":"user",
             "content":prompt
             },    
        ],
        model="gpt-3.5-turbo"
    )

    response_message = chat_completion.choices[0].message.content
    
    prompt = "' "+ message_text + " ' yazısından 2 kelimeli başlık oluştur"
    chat_completion = client.chat.completions.create(
        messages = [
            {
                "role":"user",
             "content":prompt
             },    
        ],
        model="gpt-3.5-turbo"
    )

    baslik= ""
    baslik_gpt = chat_completion.choices[0].message.content
    print("baslik: " + baslik_gpt)
    print("chat_id: " + chat_id)
    #read baslik from Chat where id is chat_id
    with db.engine.connect() as con:
        result = con.execute("SELECT baslik FROM Chat WHERE id = " + chat_id).fetchone()
        if result == None:
            return jsonify({"message": "Chat not found"})
        baslik = result[0]
    if baslik == "New Chat":
        with db.engine.connect() as con:
            con.execute("UPDATE Chat SET baslik = '" + baslik_gpt + "' WHERE id = " + chat_id)
    
    #update chat_history in Chat where id is chat_id with adding response_message
    
    with db.engine.connect() as con:
        result = con.execute("SELECT chat_history FROM Chat WHERE id = " + chat_id)
        chat_history = result.fetchone()[0]
        chat_history += message_text + " /c " + response_message + " /c "
        con.execute("UPDATE Chat SET chat_history = '" + chat_history + "' WHERE id = " + chat_id)
    
    return jsonify({"message": response_message})
    