from openai import OpenAI

client = OpenAI(
    api_key="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"
)

prompt = "Whats the most popular ski resort in Europe?"

chat_completion = client.chat.completions.create(
    messages = [
        {
            "role":"user",
         "content":prompt
         },    
    ],
    model="gpt-3.5-turbo"
)

print(chat_completion.choices[0].message.content)

