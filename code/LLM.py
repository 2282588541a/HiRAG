#change this to your api, this is for the chagpt in the paper,the main part LLM
import random
import time
from openai import OpenAI
#clinent1 is the model for most part and client2 is the model for the decompose part
client1 = OpenAI(
   api_key="xxxxxxxxx",
    base_url="https://api.openai.com/v1",
)
client2 = OpenAI(
    api_key="xxxxxxxxxx",
    base_url="https://integrate.api.nvidia.com/v1",
)

def multichat(message):
    # you can change this part to your own llm
    # The variable passed in is a string that is the part of the user that communicates with the LLM,
    #  the result returned is a string that is the result of the assistant output by the LLM
    num123=0
    while num123<10:
        try:
            chat_completion = client1.chat.completions.create(
                    messages=[
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                stream=False,
                    model="gpt-3.5-turbo")#your model
            return chat_completion.choices[0].message.content
        except Exception as e:
            print(e)
            num123=num123+1
            time.sleep(10)
    print('too many errors in gpt3.5,exit')
    exit()

def decomposechat(message):
    # this part is only used for the decompose part
    # The variable passed in is a #list that is the part of the user that communicates with the LLM,
    #  the result returned is a string that is the result of the assistant output by the LLM
    
    num123=0
          
        
    while num123<10:
        try:

            chat_completion = client2.chat.completions.create(
                messages=message,
            stream=False,
                model="meta/llama3-70b-instruct")
            return chat_completion.choices[0].message.content
        except Exception as e:
            print(e)
            num123=num123+1
            time.sleep(random.randint(10,30))
    print('too many errors in llama3,exit')
    exit()