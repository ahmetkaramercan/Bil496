from flask import Blueprint, Flask, render_template, request, jsonify, flash, redirect, url_for
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
    #chat_id = -1
    chat_history = ""
    other_chats = []
    all_chats = []
    max_chat_id = 0

    all_chats = Chat.query.filter_by(user_id=current_user.id).all()

    if request.method == 'POST': 
        current_chat_id = request.form.get('chat_id')
        print("Home sayfasına tekrar request atıldı Home chat_id :  " ,  current_chat_id)

        """if str(current_chat_id) == str(0): # yeni chat olusturmak icin
            print("current_chat_id in: " + current_chat_id)
            other_chats.append([max_chat_id, "New Chat", "Yeni bir chat oluştur"]) #!!gerek var mı bu satıra db den çekmiyor mu zaten
            current_chat_id = createNewChat()

        else: # Chat id ye karsilik gelen chati bul
            print("current_chat_id out: " + current_chat_id)
            for chat in all_chats:
                if str(chat.id) == str(current_chat_id):
                    chat_history = chat.chat_history
                    break
        
        for chat in all_chats: #other chatlari veri tabanından cek
            other_chats.append([chat.id, chat.baslik, chat.kisa_aciklama])

        chat_history = getChatHistoryFormat(chat_history)"""

        return redirect(url_for('views.homeChat', chat_id = current_chat_id))
    
    else: 
        print("chat_id in home: yok")
        if len(all_chats) <1:  # hic chat yoksa
            other_chats.append([max_chat_id, "New Chat", "Yeni bir chat oluştur"])
            current_chat_id= createNewChat()

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
                current_chat_id = last_chat.id
            
            for chat in all_chats:
                other_chats.append([chat.id, chat.baslik, chat.kisa_aciklama])  
        
        chat_history = getChatHistoryFormat(chat_history)
    
        return render_template("index.html", user=current_user, chat_id = current_chat_id, chats = chat_history, other_chats = other_chats)



@views.route("/chat", methods=['GET', 'POST'])
@login_required
def homeChat(chat_id):
    print(current_user)
    #chat_id = -1
    chat_history = ""
    other_chats = []
    all_chats = []
    max_chat_id = 0

    all_chats = Chat.query.filter_by(user_id=current_user.id).all()

    current_chat_id = chat_id
    print("Home sayfasına tekrar request atıldı Home chat_id :  " ,  current_chat_id)

    if str(current_chat_id) == str(0): # yeni chat olusturmak icin
        print("current_chat_id in: " , current_chat_id)
        other_chats.append([max_chat_id, "New Chat", "Yeni bir chat oluştur"]) #!!gerek var mı bu satıra db den çekmiyor mu zaten
        current_chat_id = createNewChat()

    else: # Chat id ye karsilik gelen chati bul
        print("current_chat_id out: " , current_chat_id)
        for chat in all_chats:
            if str(chat.id) == str(current_chat_id):
                chat_history = chat.chat_history
                break
    
    for chat in all_chats: #other chatlari veri tabanından cek
        other_chats.append([chat.id, chat.baslik, chat.kisa_aciklama])

    chat_history = getChatHistoryFormat(chat_history)

    return render_template("index.html", user=current_user, chat_id = current_chat_id, chats = chat_history, other_chats = other_chats)


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
    print("chat_id: " + chat_id)

    #update baslik ve chat_history 
    chat = Chat.query.filter_by(id=chat_id).first()
    if chat is None:
        return jsonify({"message": "Chat not found"})
    
    if chat.baslik == "New Chat": # baslik yoksa baslik olustur
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
        chat.baslik = baslik_gpt  # `baslik` özelliğini yeni değerle güncelleyin
        baslik_gpt = chat_completion.choices[0].message.content
        print("baslik: " + baslik_gpt)

    chat.chat_history += message_text + " /c " + response_message + " /c "
    db.session.commit()
    
    return jsonify({"message": response_message})


def createNewChat ():
    date = datetime.datetime.now()   
    chat_history = "selam nasılsın ? Nasıl yardımcı olabilirim ? /c "
    max_chat_id = maxChatId()
    new_kurs = Chat(id=max_chat_id,user_id=current_user.id, baslik = "New Chat", date= date, kisa_aciklama = "Yeni bir chat oluştur", chat_history = chat_history.replace("'", "''"))
    db.session.add(new_kurs)
    db.session.commit()
    return max_chat_id

def getChatHistoryFormat(str_chat_history):
    chat_history_splitted = str_chat_history.split("/c")
    chat_history = []

    for i in range(len(chat_history_splitted)-1):
        if i % 2 == 0:
            chat_history.append([0, chat_history_splitted[i]])
            print(chat_history[i])
        else:
            chat_history.append([1, chat_history_splitted[i]])
            print(chat_history[i])

    return chat_history


#yalnış çalışıyor str gibi ekliyor
#yalnış çalışıyor str gibi ekliyor
#yalnış çalışıyor str gibi ekliyor
#yalnış çalışıyor str gibi ekliyor
#yalnış çalışıyor str gibi ekliyor
#yalnış çalışıyor str gibi ekliyor
def maxChatId():
    with open("bitirme/max.txt", "r") as file:
        max_chat_id = int(file.read())
        file.close()
    #write to max.txt to update max chat id
    with open("bitirme/max.txt", "w") as file:
        file.write(str(max_chat_id + 1))
        file.close()

    return max_chat_id
    