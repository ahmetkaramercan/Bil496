from flask import Blueprint, Flask, render_template, request, jsonify, flash, redirect, url_for
import time
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, Chat
import os
from . import db
import secrets
import datetime
from PIL import Image #fotoğrafları gösterirken lazım

from openai import OpenAI
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import heapq
import numpy as np
import torch.nn.functional as F

model_path = "model"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSequenceClassification.from_pretrained(model_path)


client = OpenAI(
    api_key="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"
)

views = Blueprint('views', __name__)

@views.route("/about")
@login_required
def about():
    return render_template("about.html", user=current_user)


@views.route("/account_settings", methods=['GET', 'POST'])
@login_required
def account_settings():
    if request.method == 'POST':

        email = request.form.get('email')
        if not email: 
            email = current_user.email
        isim = request.form.get('firstName')
        if not isim: 
            isim = current_user.first_name
        soy_isim = request.form.get('lastName')
        if not soy_isim:
            soy_isim = current_user.last_name

        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.id != current_user.id:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(isim) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif len(soy_isim) < 2:
            flash('Last name must be greater than 1 character.', category='error')
        elif len(password1) > 2 and password1 != password2:
                flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            current_user.first_name = isim
            current_user.last_name = soy_isim
            current_user.email = email
            if len(password1) > 2 and password1 == password2:
                current_user.password = generate_password_hash(password1, method='pbkdf2:sha256')
            db.session.commit()
            flash('Hesap ayarları güncellendi!', category='success')
            return redirect(url_for("views.account_settings", user = current_user))

    return render_template("account_settings.html", user = current_user)



@views.route("/delete_account", methods=['GET', 'POST'])
@login_required
def delete_account():
    if request.method == 'POST':

        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        if len(password1) > 2 and password1 != password2:
            flash('Passwords don\'t match.', category='error')
    
        if check_password_hash(current_user.password, password1):
            
            Chat.query.filter_by(user_id=current_user.id).delete()
        
            user_to_delete = User.query.get(current_user.id)  # current_user'ın veritabanı modeline dönüşümü
            if user_to_delete:
                db.session.delete(user_to_delete)
            db.session.commit()
            #current_user.logout_user()
            return redirect(url_for('auth.logout'))
        
            #return redirect(url_for("auth.login"))

    return render_template("delete_account.html", user = current_user)


@views.route("/", methods=['GET', 'POST'])
@login_required
def home():
    print(current_user)
    chat_history = "Wolcome to AI Doctor! I am waiting for your symptoms. /c "
    other_chats = []
    all_chats = []
    print("home: ilk giris id yok")

    all_chats = Chat.query.filter_by(user_id=current_user.id).all()

    if len(all_chats) <1:  # hic chat yoksa
        current_chat_id= createNewChat()
        other_chats.append([current_chat_id, "New Chat", "Waiting for detailed symptoms."])

    else:   #find last chat history from all_chats which user id is current_user.id and date is max
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



@views.route("/chat/<chat_id>", methods=['GET', 'POST'])
@login_required
def homeChat(chat_id):
    print(current_user)
    print("Homechat chat_id: ", chat_id)

    chat_history = "Wolcome to AI Doctor! I am waiting for your symptoms. /c "
    other_chats = []
    all_chats = []
    deleteChat = False
    if chat_id[0] == "-":
        chat_id = int(chat_id[1:])
        deleteChat = True
        chat_to_delete = Chat.query.get(chat_id)
        if chat_to_delete and chat_to_delete.user_id == current_user.id:
            db.session.delete(chat_to_delete)
            db.session.commit()
    else:
        chat_id = int(chat_id)
    print("chat_id: " , chat_id)

    all_chats = Chat.query.filter_by(user_id=current_user.id).all()
    chat_id = chat_id


    if deleteChat:
        

        last_chat = None
        for chat in all_chats:
            if last_chat == None:
                last_chat = chat
            elif chat.date > last_chat.date:      
                last_chat = chat
        if last_chat != None:
            chat_history = last_chat.chat_history
            chat_id = last_chat.id
        print("-----------------------" , chat_id)  
        
    elif str(chat_id) == str(0): # yeni chat olusturmak icin
        chat_id = createNewChat()
        other_chats.append([chat_id, "New Chat", "Waiting for detailed symptoms."]) #!!gerek var mı bu satıra db den çekmiyor mu zaten

    else: # Chat id ye karsilik gelen chati bul
        print("chat_id out: " , chat_id)
        for chat in all_chats:
            if str(chat.id) == str(chat_id):
                chat_history = chat.chat_history
                break
    
    for chat in all_chats: #other chatlari veri tabanından cek
        other_chats.append([chat.id, chat.baslik, chat.kisa_aciklama])

    chat_history = getChatHistoryFormat(chat_history)

    return render_template("index.html", user=current_user, chat_id = chat_id, chats = chat_history, other_chats = other_chats)


@views.route("/send_message", methods=['POST'])
@login_required
def send_message():
    message_text = request.form['message']
    chat_id = request.form['chat_id']
    
    
    # Obtain all Symptoms from the message with GPT-3
    prompt = "' "+message_text+" ' If there are symptoms related to a disease in this message, list them by separating them with commas. Provide them to me in this format only: 'Symptoms: ....,....,'. If the message does not contain any symptoms, just write 'No' to me."
    chat_completion = client.chat.completions.create(
        messages = [
            {
                "role":"user",
             "content":prompt
             },    
        ],
        model="gpt-3.5-turbo"
    )
    symptoms = message_text
    print("Symptoms: ", symptoms)
    print("chat_completion.choices[0].message.content:", chat_completion.choices[0].message.content)
    
    # Predict the disease with the symptoms with custom model
    inputs = tokenizer(symptoms, return_tensors="pt")
    inputs.to(torch.device("cuda" if torch.cuda.is_available() else "cpu"))
    with torch.no_grad():
        outputs = model(**inputs)

    predicted_label_id = torch.argmax(outputs.logits[0]).item()
    predicted_disease = model.config.id2label[predicted_label_id]

    print("Predicted label:", predicted_disease)
    print("chat_id: " + chat_id)
    
    response_message =" "
    
    probabilities = F.softmax(outputs.logits, dim=1)
    top_k = 3
    probs = probabilities.cpu().numpy()
    top_k_idx = np.argsort(probs[0])[-top_k:][::-1]
    for i in range(top_k):
        print(f"{model.config.id2label[top_k_idx[i]]}: {probs[0][top_k_idx[i]]*100:.2f}%")
    
    # if predicted_disease contains "No", print "No disease"
    
    if "No" in chat_completion.choices[0].message.content:
        print("No disease")
        response_message = "I am AI doctor. Give me information about the symptoms of the disease."
    else:
        print("probs[0][top_k_idx[0]: ", probs[0][top_k_idx[0]])
        if probs[0][top_k_idx[0]] > 0.5:
            prompt = "' " + model.config.id2label[top_k_idx[0]] + " ' give me traitments for this disease. and return to me in this format: 'Until your appointment with the doctor, you can apply the following treatments: ...'."
            chat_completion = client.chat.completions.create(
                messages = [
                    {
                        "role":"user",
                     "content":prompt
                     },    
                ],
                model="gpt-3.5-turbo"
            )
            response_message = "Predicted Disease: " + model.config.id2label[top_k_idx[0]] + " <br> Probability: %" + f"{probs[0][top_k_idx[0]]*100:.2f}" + " <br> " + chat_completion.choices[0].message.content
        else:
            response_message = "Predicted Diseases: " + model.config.id2label[top_k_idx[0]] + " " + f"{probs[0][top_k_idx[0]]*100:.2f}%" + " " + model.config.id2label[top_k_idx[1]] + " " + f"{probs[0][top_k_idx[1]]*100:.2f}%" + " " + model.config.id2label[top_k_idx[2]] + " " + f"{probs[0][top_k_idx[2]]*100:.2f}%"+ ". I can not predict the disease with high probability. Please provide more information about the symptoms of the disease with privious symptoms."
            

    
    
    #update baslik ve chat_history 
    chat = Chat.query.filter_by(id=chat_id).first()
    if chat is None:
        return jsonify({"message": "Chat not found"})
    
    if chat.baslik == "New Chat" and (probs[0][top_k_idx[0]] > 0.5): # baslik yoksa baslik olustur
        baslik = model.config.id2label[top_k_idx[0]]
        chat.baslik = baslik  # `baslik` özelliğini yeni değerle güncelleyin
        print("baslik: " + baslik)
        chat.kisa_aciklama = "Get well soon!"

    chat.chat_history += message_text + " /c " + response_message.replace("<br>","\n\n") + " /c "
    db.session.commit()
    
    return jsonify({"message": response_message})


def createNewChat ():
    date = datetime.datetime.now()   
    chat_history = "Wolcome to AI Doctor! I am waiting for your symptoms. /c "
    max_chat_id = maxChatId()
    new_kurs = Chat(id=max_chat_id,user_id=current_user.id, baslik = "New Chat", date= date, kisa_aciklama = "Waiting for detailed symptoms.", chat_history = chat_history.replace("'", "''"))
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

def maxChatId():
    with open("bitirme/max.txt", "r") as file:
        max_chat_id = int(file.read())
        file.close()
    #write to max.txt to update max chat id
    with open("bitirme/max.txt", "w") as file:
        file.write(str(max_chat_id + 1))
        file.close()

    return max_chat_id











def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_picture(form_picture):
    random_hex = secrets.token_hex(8) #dosya isimlerinde karisiklik yasanmamasi icin
    _, f_ext = os.path.splitext(form_picture.filename) #dosyanin extensionunu alıyor yani png jpg gibi
    picture_fn = random_hex + f_ext #artik resim dosyasinin ismi unique ve extensionu da var misal 1865csd5f8sd.jpg gibisinden
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn) # image icin roottan başlayan path olusturuyor

    output_size = (250, 250)  #burasi ve asagisi resmi resizelayabilmek icin var bunun icin package called PILLOW kullanıyoruz
    i = Image.open(form_picture)  #pip install PIL falan yapmak gerekiyor yani
    i.thumbnail(output_size)
    i.save(picture_path) #pathe resize edilmis resmi kaydediyor yani static/profilepics klasörüne

    return picture_fn  #resim dosyasinin ismini dönüyor

def save_picture2(form_picture):
    random_hex = secrets.token_hex(8) #dosya isimlerinde karisiklik yasanmamasi icin
    _, f_ext = os.path.splitext(form_picture.filename) #dosyanin extensionunu alıyor yani png jpg gibi
    picture_fn = random_hex + f_ext #artik resim dosyasinin ismi unique ve extensionu da var misal 1865csd5f8sd.jpg gibisinden
    picture_path = os.path.join(app.root_path, 'static/kurs_pics', picture_fn) # image icin roottan başlayan path olusturuyor

    output_size = (125, 125)  #burasi ve asagisi resmi resizelayabilmek icin var bunun icin package called PILLOW kullanıyoruz
    i = Image.open(form_picture)  #pip install PIL 
    i.thumbnail(output_size)
    i.save(picture_path) #pathe resize edilmis resmi kaydediyor yani static/kurs_pics klasörüne

    return picture_fn  #resim dosyasinin ismini dönüyor

@views.route('/foto_settings', methods=['GET', 'POST'])
@login_required
def update_foto():
    if request.method == 'POST':
        looking_for = request.form.get('arama')
        if looking_for:
            return redirect(url_for('views.arama', looking_for = looking_for))
        img = request.files['image']
        if img.filename == '':
            flash('Profil resmi için dosya seçilmedi!', category ='error')
            return redirect(request.url)
        if img and allowed_file(img.filename):
            filename = save_picture(img)
            current_user.image_file = filename
            db.session.commit()
            flash('Profil resmi değiştirildi!', category ='success')
            return render_template("foto_settings.html", user = current_user)
    return render_template("foto_settings.html", user = current_user)
    