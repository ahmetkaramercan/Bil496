from flask import Blueprint, Flask, render_template, request, jsonify, flash, redirect
import time
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, Chat
import os
from . import db
import secrets
#from PIL import Image #fotoğrafları gösterirken lazım
#import openai

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
    if request.method == 'POST': 
        chat_id = request.form.get('chat_id')
        print(chat_id)
        
        #gpt den cevap"""
    # SQL sorgusu
    """chat_history = db.engine.execute("SELECT Chat.id,baslik,date,kisa_aciklama, (chat_history (tanımlamadık))"+
            " FROM Chat, User" +
            " WHERE chat.user_id = User.id """ """# AND chat.id IN (== demek)" +
            " ORDER BY COUNT(*)" +
            " DESC LIMIT 5)")
            """

  
    
    chat_history = [[0, "selam nasılsın ? Nasıl yardımcı olabilirim ?"], [1,"Saçma sapan cümleler kur"], [0, "cevap 1 asdasdadasdadsadasdasasdasdasdasdasdas asd asd asd as dasdasdasda sdas dasd asdadasdasdasd"], [1, "Teşekkür ederim"]]
    if message_text != None:
        chat_history.append([0, message_text + "  senden naber"])
    other_chats = [[4,"Hava durumu", "bugünün verilerine göre hava durumu ..."],[5,"chat 2", "asdasd asd.as.das as..."],[6,"chat 3", "cqwdasd asda sdasd asd..."]]

    return render_template("index.html", user=current_user, chat_id= 3, chats = chat_history, other_chats = other_chats)


@views.route("/send_message", methods=['POST'])
@login_required
def send_message():
    message_text = request.form['message']
    chat_id = request.form['chat_id']
    print(message_text)
    print(chat_id)
    time.sleep(5)
    # GPT ye sorgu atma kısmını burada yap
    """
    openai.api_key = "satın alcaz siteden oluşturcaz"

    response = openai.Completion.create(
        engine="gpt-3.5",
        prompt="Merhaba, benim adım ChatGPT. Sana nasıl yardımcı olabilirim?",
        max_tokens=50,
        n=1,
        stop=None,
        temperature=0.5,
    )

    message = response.choices[0].text
    print(message)
    """
    response_message = "Bu bir örnek cevaptır."
    return jsonify({"message": response_message})
    