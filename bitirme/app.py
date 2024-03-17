from flask import Flask, render_template, request, jsonify
import requests
import time


app = Flask(__name__)
app.static_folder = 'static'
#app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


@app.route("/")
def home():
    message_text = None
    """if request.method == 'POST':  # chatlar arası dolaşmanın yapılacağı zaman açılcak
        message_text = request.form.get('message')
        print(message_text)
        
        #gpt den cevap"""

    #veri tabanı işlemleri
    current_user= "1"
    chat_history = [[0, "selam nasılsın ? Nasıl yardımcı olabilirim ?"], [1,"Saçma sapan cümleler kur"], [0, "cevap 1 asdasdadasdadsadasdasasdasdasdasdasdas asd asd asd as dasdasdasda sdas dasd asdadasdasdasd"], [1, "Teşekkür ederim"]]
    if message_text != None:
        chat_history.append([0, message_text + "  senden naber"])
    other_chats = [["Hava durumu", "bugünün verilerine göre hava durumu ..."],["chat 2", "asdasd asd.as.das as..."],["chat 3", "cqwdasd asda sdasd asd..."]]

    return render_template("index.html", user=current_user, chats = chat_history, other_chats = other_chats)


@app.route("/send_message", methods=['POST'])
def send_message():
    message_text = request.form['message']
    print(message_text)
    time.sleep(5)
    # Burada GPT-3'e mesaj gönderme işlemini yapın
    # Örnek olarak sabit bir cevap döndürüldü
    response_message = "Bu bir örnek cevaptır."
    return jsonify({"message": response_message})
    


@app.route("/about")
def about():
    return render_template("about.html")




if __name__ == "__main__":
    app.run(debug=True)
