#%%
##2024.5.29 本地检索版本 更换分解器为llama3 70b ,生成器仍然是gpt 2wiki 增加轮次记录
# ret_prompt='''You need to answer the question with the retrival information and some other's response.if you don't know the answer, you can say"I don't know".
#    '''
direct_prompt='''You need to answer the question with the some information.if you don't know the answer, you can say"I don't know". Examples are as follows:
    ##question:what is the director of film Polish-Russian War (Film)?
    ##output:the director of film Polish-Russian War (Film) is Xawery \u017bu\u0142awski
    ##question:what is the director of film  Dune: Part Two
    ##output:I don't know


    ##question:'''
find_prompt='''I need you to extract the subject from the question, and I'll tell you the question and ask you to return the subject. Your response should contain only the answer and nothing else.Examples are as follows:
##question:Who is the director of Jaws？
##output:Jaws

##question:Where is Steven Spielberg from?
##output:Steven Spielberg

##question:what is the date of death of Elio Petri?
##output:Elio Petri

##question:what is the date of death of Franco Rossi (director)?
##output:Franco Rossi (director)

##question:
'''
cot_prompt='''# Question Decomposition Specialist

## Background
- You are an expert at analyzing problems and are good at breaking down difficult problems into simple problems.
- A person facing the problem {question} is asking you for help. The question is hard to answer directly.

## Goal
Helping the user decompose the question and tell the user at the right time that the problem can be solved.

## Constraint
- Forget all the knowledge you've learned before and decide whether to continue decomposing the question based only on the user's answers.
- To make it easier for the user to answer, only one simple question is asked at once.
- You can only decompose the question, do not answer it directly.

## Workflow
1. Analyse the original complex question and formulate a simple question based on that complex question.
2. Receive the user's answer to the simple question at hand.
2.1 If the user is unable to answer the current simple question, rephrase a simple question.
2.2 If the user answers the current simple question, analyze all currently known simple questions and user responses.
2.2.1 If you think that all the currently known simple questions and answers are sufficient to answer the initial complex question, say "That's enough."
2.2.2 Otherwise, ask a new simple question.
3. Repeat step 2 until the complex question can be answered.

## Example
- Complex Question: What is the award that the director of film Wearing Velvet Slippers Under A Golden Umbrella won?
- Progress of Decomposition:
	1st Simple Question: Who is the director of film Wearing Velvet Slippers Under A Golden Umbrella won?
	1st Answer: the director of film Wearing Velvet Slippers Under A Golden Umbrella won is Wunna.
	2nd Simple Question: What awards has Wunna won?
	2nd Answer: Wunna won Myanmar Motion Picture Academy Awards.
- Final Output: That's enough.

- Complex Question: Are North Marion High School (Oregon) and Seoul High School both located in the same country?
- Progress of Decomposition:
    1st Simple Question: what country is North Marion High School (Oregon) located in?
    1st Answer:North Marion High School (Oregon) is  located in United States.
	2nd Simple Question:what country is Seoul High School located in?
	2nd Answer:Seoul High School is located in South Korea.
- Final Output: That's enough.

- Complex Question:Who is the maternal grandfather of Antiochus X Eusebes?
- Progress of Decomposition:
    1st Simple Question: Who is the mother of Antiochus X Eusebes?
    1st Answer:the mother of Antiochus X Eusebes is Cleopatra IV.
	2nd Simple Question:who is the father of Cleopatra IV?
	2nd Answer:the father of Cleopatra IV is Ptolemy VIII Physcon.
- Final Output: That's enough.

- Complex Question:Where was the place of death of Anastasia Of Serbia's husband?
- Progress of Decomposition:
    1st Simple Question: Who is the husband of Anastasia Of Serbia?
    1st Answer:the husband of Anastasia Of Serbia is Stefan Nemanja.
	2nd Simple Question:Where was the place of death of Stefan Nemanja?
	2nd Answer:the place of death of Stefan Nemanja is Holy Monastery Hilandar, Moni Chilandariou, Greece.
- Final Output: That's enough.

- Complex Question:Which film has the director died earlier, Condemned Women or Faces In The Dark?
- Progress of Decomposition:
    1st Simple Question: What is the director of the film Condemned Women?
    1st Answer:the director of the film Condemned Women is Lew Landers.
	2nd Simple Question:What is the director of the film Faces In The Dark?
	2nd Answer:the director of the film Faces In The Dark is David Eady.
	3st Simple Question: When did Lew Landers die?
    3st Answer:Lew Landers die on 16 December 1962.
    4st Simple Question: When did David Eady die?
    4st Answer:David Eady die on April 5, 2009.
- Final Output: That's enough.

## Initialization
Now, a first simple question.
'''
ans_prompt='''you should answer the question with the konwn information .You should first analyze the question and the konwn information given and finally give the answer.Let's think step by step
##question:Who is the mother of the director of film Polish-Russian War (Film)?
##konwn information:The director of Polish-Russian War is Xawery Żuławski., Xawery Žuławski's mother is Małgorzata Braunek.
##output:Step 1: Analyze the Question 
The question asks for the mother of the director of the film "Polish-Russian War (Film)." 

Step 2: Analyze the Known Information
We know that the director of the film "Polish-Russian War (Film)" is Xawery Żuławski. Additionally, we are given that Xawery Żuławski's mother is Małgorzata Braunek.

Step 3: Answer the Question
Based on the known information, the mother of the director of the film "Polish-Russian War (Film)" is Małgorzata Braunek.
##question:Which film came out first, Blind Shaft or The Mask Of Fu Manchu?
##konwn information:the publication date of Blind Shaft is 2003., the publication date of The Mask Of Fu Manchu is 1932.
##output:Step 1: Analyze the Question
The question asks which film, "Blind Shaft" or "The Mask Of Fu Manchu," was released first.

Step 2: Analyze the Known Information
We know that "Blind Shaft" was released in 2003, and "The Mask Of Fu Manchu" was released in 1932.

Step 3: Answer the Question
Based on the known information, "The Mask Of Fu Manchu" came out first, in 1932, while "Blind Shaft" was released in 2003.

##question:'''
is_ans_prompt='''I will tell you the question,correct answer and response. You need to judge whether the response is correct.If the answer is correct ,return yes,else,return no. Examples are as follows:
question:Who is the mother of the director of film Polish-Russian War (Film)?
correct answer:Jagna Žuławski
response:Jagna Žuławski
output:yes
'''
exact_prompt='''Based on the input , you have to find the answer,which usually on the behind of the "Answer:"
input:1. Analyzing the Question:
   - The question seeks to identify the director of the film "Polish-Russian War (Wojna polsko-ruska)."
   - The known information provided is that the film was directed by Xawery Żuławski.
   - Additionally, it's mentioned that the film is based on the novel "Polish-Russian War under the white-red flag" by Dorota Masłowska.

2. Known Information:
   - The director of the film is Xawery Żuławski.
   - The film is based on the novel by Dorota Masłowska.

3. Answer:
   - The director of the film "Polish-Russian War (Wojna polsko-ruska)" is Xawery Żuławski.
output: The director of the film "Polish-Russian War (Wojna polsko-ruska)" is Xawery Żuławski.
input: 1: Analyze the Question
The question asks which film, "Blind Shaft" or "The Mask Of Fu Manchu," was released first.

Step 2: Analyze the Known Information
We know that "Blind Shaft" was released in 2003, and "The Mask Of Fu Manchu" was released in 1932.

Step 3: Answer the Question
Based on the known information, "The Mask Of Fu Manchu" came out first, in 1932, while "Blind Shaft" was released in 2003.
output: Based on the known information, "The Mask Of Fu Manchu" came out first, in 1932, while "Blind Shaft" was released in 2003.

'''
exact_prompt2='''Based on the input and the question, you have to tell me the answer.Answers should be concise and contain only the corresponding keywords
##input:The director of the film "Polish-Russian War (Wojna polsko-ruska)" is Xawery Żuławski
##question:what is the director of film Polish-Russian War (Film)?
##output:Xawery Żuławski

##input:The director of Xawery Żuławski is Małgorzata Braunek
##question:Who is the mother of Xawery Żuławski?
##output:Małgorzata Braunek

##input:'''
exact_prompt3='''Based on the input and the question, you have to tell me the answer.Answers should be concise and contain only the corresponding keywords
##input:The director of the film "Polish-Russian War (Wojna polsko-ruska)" is Xawery Żuławski
##question:what is the director of film Polish-Russian War (Film)?
##output:Xawery Żuławski

##input:The director of Xawery Żuławski is Małgorzata Braunek
##question:Who is the mother of Xawery Żuławski?
##output:Małgorzata Braunek

##input:Venice's country is Italy while Los Angeles's country is the United States
##question:Are Venice and Los Angeles in the same country?
##output:No

##input:Venice's country is Italy while Los Angeles's country is the United States
##question:Are Venice and Los Angeles in the same country?
##output:No

##input:'''
ret_prompt='''you should answer the question with the konwn information .You should first analyze the question and the konwn information given and finally give the answer.Let's think step by step!
##question:Who is the director of film Polish-Russian War (Film)?
##konwn information:Polish-Russian War (Wojna polsko-ruska) is a 2009 Polish film directed by Xawery Żuławski based on the novel Polish-Russian War under the white-red flag by Dorota Masłowska.
##output:1. Analyzing the Question:
   - The question seeks to identify the director of the film "Polish-Russian War (Wojna polsko-ruska)."
   - The known information provided is that the film was directed by Xawery Żuławski.
   - Additionally, it's mentioned that the film is based on the novel "Polish-Russian War under the white-red flag" by Dorota Masłowska.

2. Known Information:
   - The director of the film is Xawery Żuławski.
   - The film is based on the novel by Dorota Masłowska.

3. Answer the Question:
   - The director of the film "Polish-Russian War (Wojna polsko-ruska)" is Xawery Żuławski.

##question:Who is the mother of Xawery Żuławski?
##konwn information:Xawery Żuławski (born 22 December 1971 in Warsaw) is a Polish film director.

In 1995 he graduated National Film School in Łódź. He is the son of actress Małgorzata Braunek and director Andrzej Żuławski. His second feature Wojna polsko-ruska (2009), adapted from the controversial best-selling novel by Dorota Masłowska, won First Prize in the New Polish Films competition at the 9th Era New Horizons Film Festival in Wrocław. In 2013, he stated he intends to direct a Polish novel "Zły" by Leopold Tyrmand.
##output:1. Analyzing the Question:
   - The question seeks to identify the mother of Xawery Żuławski.
   - The known information provided includes Xawery Żuławski's birthdate, occupation as a Polish film director, and details about his education and career.
   - It's mentioned that his mother is an actress named Małgorzata Braunek and his father is a director named Andrzej Żuławski.

2. Known Information:
   - Xawery Żuławski was born on December 22, 1971, in Warsaw, Poland.
   - He is a Polish film director.
   - His mother is actress Małgorzata Braunek.
   - His father is director Andrzej Żuławski.

3. Answer the Question:
   - The mother of Xawery Żuławski is Małgorzata Braunek.


'''

can_answer_prompt='''Based on the input and the question, you have to tell me if you can answer the question.Your answer must be yes or no
##input:The spouse of Grand Duke Kirill Vladimirovich of Russia is not known.
##question:what is the spouse of Grand Duke Kirill Vladimirovich of Russia?
##output:no

##input:The director of the film "Thomas Jefferson" is Ken Burns.
##question:what is the director of Thomas Jefferson(Film)?
##output:yes


##input:'''

revise_prompt=''' you are given a question ,some information and a subquestion. the subquestion may have some fault,you need to correct it .Examples are as follows:
##question:Who is the mother of the director of film Polish-Russian War (Film)?
##konwn information:The director of Polish-Russian War is Xawery Żuławski.
##subquestion:Who is the mother of Xawery Żułwski?
##output:Who is the mother of Xawery Żuławski?


'''
choose_prompt='''Based on the ithe question and information, you must return yes or no.
remeber:you must return yes or no
'''
google_entity_prompt='''You need to describe an entity in a information.I will give you the entity and information,You need to describe an entity based the information .examples are as follows:
##entity:Xawery Żuławski
##information:The director of the film "Polish-Russian War (Wojna polsko-ruska)" is Xawery Żuławski.
##output:Xawery Żuławski is the director of the film "Polish-Russian War (Wojna polsko-ruska)".

##entity:Małgorzata Braunek.
##information:The mother of Xawery Żuławski is Małgorzata Braunek.
##output:Małgorzata Braunek is the mother of Xawery Żuławski.



'''

exact_prompt4='''You need to extract the answer to the question from the reply. Note that only the part related to the answer is retained.
##question:Who is the director of film Polish-Russian War (Film)?
##reply:The director of the film "Polish-Russian War" is Dziga Vertov. Released in 1920, it's a Soviet silent documentary film detailing the Polish-Soviet War.Sorry,I am an artificial intelligence and do not have real-time information
##output:The director of the film "Polish-Russian War" is Dziga Vertov

##question:'''
ques_prompt='''I will give you a question and you need to return the answer,examples are as follows:
##question:what is the date of birth of Don Chaffey?
##output:the date of birth of Don Chaffey is August 5, 1917.

##question:what is the director of The Half-Way Girl?
##output:the director of The Half-Way Girl is John Francis Dillon.


##question'''
can_answer_prompt1='''Based on the known infotmation and question,You need to tell me if you can answer the question or not.If you can answer the question,return yes with answer,else return no. 
##question:Who is the mother of the director of film Polish-Russian War (Film)?
##konwn information:The director of Polish-Russian War is Xawery Żuławski., Xawery Žuławski's mother is Małgorzata Braunek.
##output:yes, Małgorzata Braunek

##question:Which film came out first, Blind Shaft or The Mask Of Fu Manchu?
##konwn information:the publication date of Blind Shaft is 2003., the publication date of The Mask Of Fu Manchu is 1932.
##output:yes, The Mask Of Fu Manchu

##question:When did John V, Prince Of Anhalt-Zerbst's father die?
##konwn information:the fatherJohn V of Anhalt-Zerbst is Ernest I, Prince of Anhalt-Dessau
##ouput:no

#question:Who is Charles Bretagne Marie De La Trémoille's paternal grandfather?
##konwn information:the father of Charles Bretagne Marie de La Trémoille is Jean Bretagne Charles de La Trémoille.the father of Jean Bretagne Charles de La Trémoille is Charles Armand René de La Trémoille.
##output:yes, Charles Armand René de La Trémoille

##question:'''
can_answer_prompt2='''Based on the question and a response from others, you have to tell me if the response can answer the question. Your answer must be yes or no.
##question: What is the date of death of Armin, Prince Of Lippe's father?
##response: Based on the known information, the date of death of Armin, Prince Of Lippe's father, Leopold IV, Prince of Lippe, is December 30, 1949.
##output: yes

##question: Which film has the director died earlier, Love In Exile or Manchi Vallaki Manchivadu?
##response: Answer: Unable to determine.
##output: no

##question: Who is the paternal grandfather of Zubdat-Un-Nissa?
##response: Based on the known information, the paternal grandfather of Zubdat-Un-Nissa is Shah Jahan.
##output: yes

##question: '''
#%%
import datetime
import pickle
from elasticsearch import Elasticsearch
from transformers import AutoTokenizer, AutoModel,AutoModelForCausalLM
from openai import OpenAI
from Levenshtein import ratio
from src.contriever import Contriever
import re
import os
import torch
import numpy as np
from bs4 import BeautifulSoup
from collections import Counter
device = 'cuda:6'
device1='cuda:4'
device2='cuda:5'
from BM25 import BM25
from retriever_wiki import BM25_1
import transformers
from transformers import GPT2TokenizerFast

client2 =[
        OpenAI(
   api_key="sk-TOFsTYkwlpkYwEjI2715Bf8c892e4aBdA249282071755f67",
    base_url="https://api.swt-ai.com/v1",
),OpenAI(
   api_key="sk-TOFsTYkwlpkYwEjI2715Bf8c892e4aBdA249282071755f67",
    base_url="https://api.swt-ai.com/v1"
)
]
apinum1=0
# client = OpenAI(
#     api_key="sk-1VC7NamOCcdb747d4866T3BLbKFJF7Eb106038fe46769427",
#     base_url="https://api.ohmygpt.com/v1",
# )
# model = AutoModelForCausalLM.from_pretrained(
#     "/datas/zhangxiaoming/model/qwen-cot",
#     torch_dtype="auto",
#     device_map=device
# )
# tokenizer = AutoTokenizer.from_pretrained("/datas/zhangxiaoming/model/qwen-cot")
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
def sendemail(message='',subject='Test Subject'):

    username = "zxm2282588541@gmail.com"
    password = "uqtqqmgzrtarcuoc"
    mail_from = "zxm2282588541@gmail.com"
    mail_to = "2282588541@qq.com"
    mail_subject = subject
    mail_body = message
    try:
        mimemsg = MIMEMultipart()
        mimemsg['From']=mail_from
        mimemsg['To']=mail_to
        mimemsg['Subject']=mail_subject
        mimemsg.attach(MIMEText(mail_body, 'plain'))
        connection = smtplib.SMTP(host='smtp.gmail.com', port=587)
        connection.starttls()
        connection.login(username,password)
        connection.send_message(mimemsg)
        connection.quit()
    except Exception as e:
        print(e)  

def receive(message):
    host = '127.0.0.1'
    port = 12346
    for i in range(0,10):
        try:
            inputs1 = ret_tokenizer(message, padding=True, truncation=True, return_tensors="pt")
            inputs1=inputs1.to('cuda')
            embeddings1 = ret_model(**inputs1).squeeze()
            arra=embeddings1.cpu().detach().numpy()
            torch.cuda.empty_cache() 
            q=torch.from_numpy(arra)
            return q
        except Exception as e:
            print(e)
            time.sleep(1)
# 创建一个logger
logger = logging.getLogger('my_logger')
logger.setLevel(logging.DEBUG)

# 创建一个handler，用于写入日志文件
fh = logging.FileHandler('output.log')
fh.setLevel(logging.DEBUG)

# 定义handler的输出格式
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)

# 给logger添加handler
logger.addHandler(fh)
endtimes1=0
LOCK_FILE = 'lock.txt'
LOCK_TIMEOUT = 2  # 锁的超时时间为60秒
def acquire_lock():
    while os.path.exists(LOCK_FILE):
        print("另一个文件正在执行,等待1秒...")
        time.sleep(1)
    open(LOCK_FILE, 'w').close()
    # 启动一个线程,在60秒后自动释放锁
    threading.Timer(LOCK_TIMEOUT, release_lock).start()

def release_lock():
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)
        # print("锁已释放")


from transformers import AutoModelForCausalLM, AutoTokenizer
device = "cuda" # the device to load the model onto

# model = AutoModelForCausalLM.from_pretrained("/data/zhangxiaoming/model/Qwen2-7B-Instruct", device_map="auto")
# tokenizer = AutoTokenizer.from_pretrained("/data/zhangxiaoming/model/Qwen2-7B-Instruct")

# prompt = "Give me a short introduction to large language model."

# messages = [{"role": "user", "content": prompt}]


# print(pipeline("Hey how are you doing today?"))


def multichat(message):
    # print("GPT3.5开始回答",message)
    num123=0
    while num123<10:
        try:
            global apinum1
            apinum1=(apinum1+1)%6
            client9=[OpenAI(
    api_key="a6000",
        base_url="http://7d8aa510.r17.cpolar.top/v1",
    )]
            chat_completion = client9[0].chat.completions.create(
                    messages=[
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                stream=False,
                    model="llama3-8b")
            return chat_completion.choices[0].message.content
        except Exception as e:
            print(e)
            print(apinum1)
            num123=num123+1
            if num123==5:
                time.sleep(700)
            time.sleep(10)

    sendemail(message=str(e),subject='GPT3.5错误')
    exit()
    # except Exception as e:
    #     print(e)    
        # while num123<10:
        #     try:
        #         global apinum1
        #         apinum1=(apinum1+1)%2
        #         acquire_lock()
        #         chat_completion = client2[apinum1].chat.completions.create(
        #             messages=[
        #             {
        #                 "role": "user",
        #                 "content": message
        #             }
        #         ],
        #         stream=False,
        #             model="mixtral-8x7b-instruct")
        #         # release_lock()
        #         # time.sleep(0.5)
        #         # print("GPT3.5回答",chat_completion.choices[0].text)
        #         return chat_completion.choices[0].message.content
        #     except Exception as e:
        #         print(e)
        #         print(apinum1)
        #         num123=num123+1
        #         time.sleep(random.randint(10,30))
        # global endtimes1
        #sendemail(message=str(e),subject='第'+str(endtimes1)+'次试图修复')
        # if(endtimes1<5):
        #     t=endtimes1
        #     time.sleep(random.randint(500,700))
        #     endtimes1=t+1
        #     return multichat(message)
        #exit()
        
def chatgpt3(num=0,message=''):
    url=''
    if num==0:
        return multichat(message)
    else:
        return multichat(message)
        

   
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer any_string_you_like'
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "user",
                "content": message
            }
        ],
        "stream": False
    }

    response = requests.post(url, headers=headers, json=data)
    # print(response.json()['choices'][0]['message']['content']) 
    return response.json()['choices'][0]['message']['content']
#并行部分开始

# tokenizer_1 = AutoTokenizer.from_pretrained("/datas/huggingface/chatglm3-6b", trust_remote_code=True)
# parallel_model_1=AutoModel.from_pretrained("/datas/huggingface/chatglm3-6b", trust_remote_code=True, device=device).eval()
# parallel_model_2=AutoModel.from_pretrained("/datas/huggingface/chatglm3-6b", trust_remote_code=True, device=device1).eval()
# parallel_model_3=AutoModel.from_pretrained("/datas/huggingface/chatglm3-6b", trust_remote_code=True, device=device1).eval()
# parallel_model_4=AutoModel.from_pretrained("/datas/huggingface/chatglm3-6b", trust_remote_code=True, device=device2).eval()
# parallel_model_5=AutoModel.from_pretrained("/datas/huggingface/chatglm3-6b", trust_remote_code=True, device=device2).eval()
# def multichat_1(message,model):
#     response, history = model.chat(tokenizer, message, history=[])
#     return response
def multichat_parallel(message,num=0):
    if num==0:
        # response, history = parallel_model_1.chat(tokenizer, message, history=[])
        # return response 
     
        ans=chatgpt3(1,message)
        print("GPT3.5回答",ans)   
        return ans
    if num==1:
        response, history = parallel_model_2.chat(tokenizer, message, history=[])
        return response
    if num==2:
        response, history = parallel_model_3.chat(tokenizer, message, history=[])
        return response
    if num==3:
        response, history = parallel_model_4.chat(tokenizer, message, history=[])
        return response
    
    response, history = parallel_model_5.chat(tokenizer, message, history=[])
    return response
def multichat_parallel1(message,num=0):#调用gpt的方案
 
        # response, history = parallel_model_1.chat(tokenizer, message, history=[])
        # return response 
        
    ans=chatgpt3(num,message)
    # print("GPT3.5回答",ans)   
    return ans

   
#%% 
# keyword_list=['','','','','']
# response_list=['','','','','']
keyword_list=['','']
response_list=['','']
# year=0##对于年份问题这里特殊处理一
# year_num=0 #年份的个数
# def parallel_chat(message,question,num):
#     response=multichat_parallel(message,num)
#     response=str(response)
#     global keyword_list
#     global response_list
#     global year
#     global year_num
#     # print("未提取子问题的答案",response)
#     for exact_num in range(0,3):#未按照COT格式输出，重新生成
#         if ('Analyzing' in response or 'Analyze' in response)and 'Known Information' in response and 'Answer' in response:
#             break
#         print("生成格式不对")
#         response=multichat_parallel(message,num)
#         response=str(response)
#         print("未提取子问题的答案",response)
#     response=exact_answer(response)
#     temp_list=re.findall(r'\b\d{4}\b', response)
#     if (len(temp_list)>0):
#         year_num=year_num+1
#         year=temp_list[0]
#     print("子问题的答案",response)
     
#     keyword=multichat_parallel(exact_prompt2+response+"\n##question:"+question+'\n'+"##output:",num) 
#     print("关键词",keyword)
#     keyword_list[num]=keyword
#     response_list[num]=response
def parallel_chat(message,question,num):
    response=multichat_parallel1(message,num)
    response=str(response)
    global keyword_list
    global response_list
    global year
    global year_num
    # print("未提取子问题的答案",response)
    for exact_num in range(0,3):#未按照COT格式输出，重新生成
        if ('Analyzing' in response or 'Analyze' in response)and 'Known Information' in response and 'Answer' in response:
            break
        print("生成格式不对")
        response=multichat_parallel1(message,num)
        response=str(response)
        print("未提取子问题的答案",response)
    response=exact_answer(response)
    # temp_list=re.findall(r'\b\d{4}\b', response)
    # if (len(temp_list)>0):
    #     year_num=year_num+1
    #     year=temp_list[0]
    print("子问题的答案",response)
     
    keyword=multichat_parallel1(exact_prompt2+response+"\n##question:"+question+'\n'+"##output:",num) 
    print("关键词",keyword)
    keyword_list[num]=keyword
    response_list[num]=response
    return response,keyword

#%%并行部分新增代码结束
import socket
import json
import torch
import threading
os.environ["http_proxy"] = "http://127.0.0.1:10101"
os.environ["https_proxy"] = "http://127.0.0.1:10101"
os.environ['API_KEY']='AIzaSyCFxtMdyQLwkzSrwBL9EpAOAkbR0CvhwQI'
# import google.generativeai as genai


# genai.configure(api_key=os.environ["API_KEY"])
# model = genai.GenerativeModel('gemini-pro')
# response = model.generate_content("Write a story about a magic backpack.")
# print(response.text)
# model2 = AutoModelForCausalLM.from_pretrained("/data/zhangxiaoming/model/Mistral-7B-Instruct-v0.2", torch_dtype=torch.float16).half()
# model2.to(device1)
# tokenizer2 = AutoTokenizer.from_pretrained("/data/zhangxiaoming/model/Mistral-7B-Instruct-v0.2")
# model2 = model2.eval()
import os
import requests
import wikipedia
lasttime=0#维基百科上次调用时间
gemini_lastime=0#gemini 上次调用时间
import time
import random
def exact_answer(mess):
    # try:
    parts = mess.split("Answer the Question", 1)

# 取出 "answer" 之后的部分
    if len(parts) > 1:
        result = parts[1]
        
    else:
        result =multichat(exact_prompt+mess) 
    return result   
def exact_answer2(mess,question):#子问题提取keyword
    return multichat(exact_prompt2+mess+"\n##question:"+question+'\n'+"##output:") 
def exact_answer3(mess,question,info):#父问题提取keyword
    return multichat(exact_prompt3+mess+'.'+info+"\n##question:"+question+'\n'+"##output:") 
def exact_answer4(mess,question):#父问题提取keyword
    return multichat(exact_prompt3+mess+"\n##question:"+question+'\n'+"##output:") 
def can_answer(mess,question):#判断问题能否被回答
    # return multichat(can_answer_prompt+mess+"\n##question:"+question+'\n'+"##output:")
    ans_num=0
    for SC in range (0,5):#self-constitency
        ans_flag=multichat(can_answer_prompt+mess+"\n##question:"+question+'\n'+"##output:")
        if 'yes' in ans_flag:
            ans_num=ans_num+1
    if ans_num>2:
        return 'yes'
    else:
        return 'no'
def can_answer1(known_info,question):#判断问题能否被回答
    ans_num=0
    for SC in range (0,5):#self-constitency
        ans_flag=multichat(can_answer_prompt1+question+"\n##konwn information:"+known_info+'\n'+"##output:")
        if 'yes' in ans_flag:
            ans_num=ans_num+1
    if ans_num>2:
        return 'yes'
    else:
        return 'no'
def can_answer2(question,response):#判断答案是否可以被采纳
    # return multichat(can_answer_prompt+mess+"\n##question:"+question+'\n'+"##output:")
    ans_num=0
    for SC in range (0,5):#self-constitency
        ans_flag=multichat(can_answer_prompt2+question+"\n##response:"+response+'\n'+"##output:")
        if 'no' in ans_flag:
            ans_num=ans_num+1
    if ans_num>2:
        return 'no'
    else:
        return 'yes'
def direct_answer(message,question):#直接回答子问题
    keyword_list=[]
    response_list=[]
    d = dict()
    for SCtime in range(0,3):
        
        response=multichat(message)
        # print("未提取的子问题答案",response)
      
        # print("子问题问题的答案",response)
        keyword=multichat(exact_prompt2+response+"\n##question:"+question+'\n'+"##output:") 
        print("子问题关键词",keyword) 
        keyword_list.append(keyword)
        response_list.append(response)
        d[keyword] = d.setdefault(keyword, 0) + 1
        
        # setdefault()函数,如果键不存在于字典中，将会添加键并将值设为默认值
    most_common_word = Counter(keyword_list).most_common(1)[0][0]        
    if d[most_common_word]<2:
        for SCtime in range(0,3):
        
            response=multichat(message)
            # print("未提取的子问题答案",response)
            response=str(response)
            
            keyword=multichat(exact_prompt2+response+"\n##question:"+question+'\n'+"##output:") 
            print("子问题关键词",keyword) 
            keyword_list.append(keyword)
            response_list.append(response)
            d[keyword] = d.setdefault(keyword, 0) + 1

    most_common_word = Counter(keyword_list).most_common(1)[0][0]

            # 找出这个单词在列表中的位置
    position = keyword_list.index(most_common_word)

    response=response_list[position]
    print("最终子问题答案",response)
    print("最终子问题关键词",most_common_word)
    return response   
def scrape_table(url, table_id='infobox vevent'):#对于带知识小窗的维基百科要及时获取答案
    # 发送请求并获取网页内容
    # return ''
    # print("tabeleurl",url)
    #return ''
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # 找到指定ID的表格
    table = soup.find('table', {'class': table_id})
    if table is None:
        table = soup.find('table', {'class': 'infobox vcard'})
    if table is None:
        table = soup.find('table', {'class': 'infobox ib-settlement vcard'})  
    if table is None:
        table = soup.find('table', {'class': 'infobox biography vcard'})          
    if table is None:
        table = soup.find('table', {'class': 'infobox vcard plainlist'})          

    if table is None:
        # print("未找到指定的表格")
        return ''

    # 提取表格中的数据
    rows = table.find_all('tr')
    data = []
    for row in rows:
        cells = row.find_all(['td', 'th'])
        row_data = []
        for cell in cells:
            row_data.append(cell.get_text(strip=True))
        data.append(row_data)
    # for row in data:
    #     print(row)   
    return ''.join(str(item) for item in data)[:6000]
def scrape_table_outline(title):
    es = Elasticsearch()
    query = {
    "query": {
        "match": {
            "title": title
        }
    }
}      
    response = es.search(index="wiki_konwinfo", body=query)
    if response["hits"]["total"]["value"] > 0:
        temp=response["hits"]["hits"][0]["_source"]['title']
        if temp==title:
            return str(response["hits"]["hits"][0]["_source"])[:6000]
        else:
            return ''
    else:
        return ''
google_time=0
def google_search(ques,retry_num=0):
    search_ques=ques
    find1=find_prompt+ques+'\n'+"##output: "
    ques=multichat(find1) #先找到主体再进行搜索
    print("开始使用谷歌搜索",ques)
    api_url = 'https://www.googleapis.com/customsearch/v1?key=AIzaSyB9Uk3R53KNMzIR_AR1ChlcfQ5RzYv5578&q='+ques+'&cx=3542d78eb7b3a49e9&start=0&num=10'
    print("API URL:", api_url)
    global google_time
    try:
        # 发送GET请求到API

        response = requests.get(api_url)
        
        # 检查请求是否成功
        if response.status_code == 200:
            # 解析JSON格式的响应数据
            data = response.json()
            
            # print("搜索结果:",data)
            if 'items' not in data:
                time.sleep(5)
                print('google fault',data)
                return google_search(ques,retry_num=retry_num)
            print('简介',data['items'][0]['snippet'])
            # print(data['items'][0]['link'])
            str1=str(data['items'][0]['link'])
            parts = str1.split("wiki/", 1)
            if len(parts) <2:
                print("分解错误")
            else:
                s = parts[1]
                s = s.replace('_', ' ')
                s = s.replace('%27', "'")
                print('维基主体',s)
            google_time=0    
            if retry_num==0:
                return data['items'][0]['snippet']+scrape_table(data['items'][0]['link'])
            else :
                return wiki_search(search_ques,s,retry_num=retry_num)
        else:
            print("请求失败，状态码:", response.status_code)
            time.sleep(10)
            google_time=google_time+1
            if google_time>1:
                find1=find_prompt+ques+'\n'+"##output: "
                ques=multichat(find1)
                try:
                    topic=wikipedia.search(ques)
                    return wiki_search(search_ques,topic[0],retry_num=retry_num)
                except Exception as e:
                    print("维基百科搜索失败",e)
                    return 'No result#^'
            return google_search(search_ques,retry_num=retry_num+1)
    except Exception as e:
        print("发生网络错误:", e)
        time.sleep(10)
        google_time=google_time+1
        if google_time>1:
            find1=find_prompt+ques+'\n'+"##output: "
            ques=multichat(find1)
            try:
                topic=wikipedia.search(ques)
                return wiki_search(search_ques,topic[0],retry_num=retry_num)
            except Exception as e:
                print("维基百科搜索失败",e)
                return 'No result#^'
            
        return google_search(search_ques,retry_num=retry_num+1)
google_cache={}    #存放缓冲的link，避免消耗大量搜索api
last_google_time=0    
# def google_search2(googleques,ques,retry_num=0,end_time=0):#使用searapi去做测试
#     # 参数分别是问题,真实问题，当前重复次数，是否是回退后的结果
#     keys=loadfile('/datas/zhangxiaoming/personal/zxmRAG/keys.json')#读取keys文件
#     temp_key=''#选取当前可用的key
#     for inst in keys:
#         if inst[1]>0:
#             temp_key=inst[0]
#             break
#     # temp_key='b140edc501979ee129d8da2379ffa3ff915513e978567c7d7ab559d5fcc52454' 
#     api_url='https://serpapi.com/search.json?engine=google&q='+googleques+'&location=Austin,%20Texas,%20United%20States&hl=en&gl=us&google_domain=google.com&api_key='+temp_key    
#     api_url=str(api_url)
#     print("当前问题是：",googleques)
#     # api_url='https://serpapi.com/search.json?q=Coffee&location=Austin,+Texas,+United+States&hl=en&gl=us&google_domain=google.com&api_key=b140edc501979ee129d8da2379ffa3ff915513e978567c7d7ab559d5fcc52454'
#     print("API URL:", api_url)
#     if retry_num==0 or (googleques not in google_cache and retry_num>1):#第一次搜索或者没有缓存
#         try:
#             # 发送GET请求到API
#             if time.time()-last_google_time<20:
#                 time.sleep(20-time.time()+last_google_time)
#             response = requests.get(api_url)
#             print("开始使用searapi谷歌搜索",googleques)
#             # 检查请求是否成功
#             if response.status_code == 200:
#                 # 解析JSON格式的响应数据
#                 data = response.json()
#                 for temp_num in range (0,len(keys)):
#                     if keys[temp_num][0]==temp_key:
#                         keys[temp_num][1]=keys[temp_num][1]-1
#                         break
#                 with open('/datas/zhangxiaoming/personal/zxmRAG/keys.json', 'w') as file:
#                     json.dump(keys, file)    
#                 # print("收到的数据",data)
#                 # print("搜索结果:",data)
#                 return_ans=''
#                 out_link=''
#                 if 'organic_results' not in data:
#                     time.sleep(5)
#                     print('google fault',data)
#                     sendemail(message=str(data),subject='google fault organic_results not in data')
#                     return google_search2(googleques,retry_num=retry_num+1,end_time=end_time)
#                 organic_results=data['organic_results']

#                 print(out_link)        
#                 if 'answer_box' in data :
#                     print('answerbox',data['answer_box'])
                    
        
#                     if 'answer' in data['answer_box'] and 'title' in data['answer_box']:
#                         ans=data['answer_box']['title']+' is '+data['answer_box']['answer']
                        
#                         return_ans=return_ans+' . '+ans  
#                     if 'snippet' in data['answer_box']:
#                         return_ans=return_ans+' . '+data['answer_box']['snippet']  
#                     if return_ans=='':
#                         https_keys = [key for key, value in data.items() if isinstance(value, str) and re.search(r'https://', value)]
#                         filtered_data = {key: value for key, value in data['answer_box'].items() if key not in https_keys}
#                         print('直接使用answerbox',filtered_data)
#                     print("谷歌问题答案",return_ans)
#                     if 'link' in data['answer_box'] :
#                             link=data['answer_box']['link']
#                             if 'en.wikipedia.org' in link:
#                                 out_link=link
                                
#                     # else:
#                     #     print('answerbox no answer')
                                                    
#                     else:
#                         if end_time==1:#第二轮不只限于维基百科了
#                             link=organic_results[0]['link']
#                             return wiki_search(ques,link,retry_num)

#                         for inst in organic_results:
#                             link=inst['link']
#                             if 'en.wikipedia.org' in link:
#                                 out_link=link
#                                 # keyword=inst['title']
#                                 # return_ans=return_ans+inst['snippet']
#                                 return_ans=return_ans+scrape_table(link)
#                                 break        
#                 else:
#                     for inst in organic_results:
#                         link=inst['link']
#                         if 'en.wikipedia.org' in link:
#                             out_link=link
#                             # keyword=inst['title']
#                             # return_ans=return_ans+inst['snippet']
#                             return_ans=return_ans+scrape_table(link)
#                             break        
#                 cache_instance={googleques:out_link}
#                 google_cache.update(cache_instance) #更新cache文件               
#                 if return_ans=='':
#                     print("outlink",out_link)
#                     if out_link=='':
#                         return google_search2(googleques=googleques,ques=ques,retry_num=retry_num+1,end_time=end_time)
#                     print('return_ans is empty')
#                     return wiki_search(ques=ques,link=out_link,retry_num=retry_num)#几乎不可能走的道路，代表当前没有任何候选项满足条件,所以更换检索器
                
#                 return_ans=return_ans+' . '
#                 print('谷歌搜索返回的最终结果',return_ans)
#                 return return_ans
#                 # print(data['items'][0]['link'])
#             else:
#                 print("请求失败，状态码:", response.status_code)   
#                 return 'No result#^'
#         except Exception as e:
#             print("发生网络错误:", e)
#             sendemail(message=str(e),subject='发生网络错误')
#             time.sleep(20)
#             search_ques=ques
#             if retry_num>1:
#                 # find1=find_prompt+ques+'\n'+"##output: "
#                 # ques=multichat(find1)
#                 # topic=wikipedia.search(ques)
#                 return wiki_search2(search_ques,retry_num=retry_num)
#             return google_search2(google_ques,ques,retry_num=retry_num+1,end_time=end_time)        
#     else:            
#             if googleques not in google_cache:#很少会出现这种情况
#                 print("缓存中没有找到")
#                 print("googlecache",google_cache)
#                 return "empty list"#重新生成问题
#             str1=google_cache[googleques]
#             if str1=='':
#                 print("缓存中为空，采用传统方案")
#                 if end_time==0:
#                     return wiki_search2(ques,retry_num=retry_num-1)#初始使用维基百科搜索时，值应该是0
#                 else:
#                     return dpr_search(ques,'',retry_num=retry_num-1)
#             if end_time==0:
#                 return wiki_search(ques,str1,retry_num=retry_num-1)
#             else:
#                 return dpr_search(ques,str1,retry_num=retry_num-1)

#以下更换api厂商      
google_times=0      
def google_search2(googleques,ques,retry_num=0,end_time=0):#使用searapi去做测试
    # 参数分别是问题,真实问题，当前重复次数，是否是回退后的结果
    # keys=loadfile('/datas/zhangxiaoming/personal/zxmRAG/keys.json')#读取keys文件
    # temp_key=''#选取当前可用的key
    # for inst in keys:
    #     if inst[1]>0:
    #         temp_key=inst[0]
    #         break
    # temp_key='b140edc501979ee129d8da2379ffa3ff915513e978567c7d7ab559d5fcc52454' 
    
    
    api_url="https://google.serper.dev/search"
    payload = json.dumps({
    "q": googleques
    })
    headers = {
    'X-API-KEY': '42e2c8b2f2c5a3561609cef23cfd3a3b696bda72',
    'Content-Type': 'application/json'
    }
    # api_url=str(api_url)
    print("当前问题是：",googleques)
    # api_url='https://serpapi.com/search.json?q=Coffee&location=Austin,+Texas,+United+States&hl=en&gl=us&google_domain=google.com&api_key=b140edc501979ee129d8da2379ffa3ff915513e978567c7d7ab559d5fcc52454'
    # print("API URL:", api_url)
    if retry_num==0 or (googleques not in google_cache and retry_num>1):#第一次搜索或者没有缓存
        try:
            # 发送GET请求到API
            if time.time()-last_google_time<20:
                time.sleep(20-time.time()+last_google_time)
            response = requests.request("POST", url=api_url, headers=headers, data=payload)
            global google_time
            google_time=google_time+1
            print("开始使用searapi谷歌搜索",googleques)
            # 检查请求是否成功
            if response.status_code == 200:
                # 解析JSON格式的响应数据
                data = response.json()
                # for temp_num in range (0,len(keys)):
                #     if keys[temp_num][0]==temp_key:
                #         keys[temp_num][1]=keys[temp_num][1]-1
                #         break
                # with open('/datas/zhangxiaoming/personal/zxmRAG/keys.json', 'w') as file:
                #     json.dump(keys, file)    
                # print("收到的数据",data)
                # print("搜索结果:",data)
                return_ans=''
                out_link=''
                if 'organic' not in data:
                    time.sleep(5)
                    print('google fault',data)
                    sendemail(message=str(data),subject='google fault organic_results not in data')
                    return google_search2(googleques,retry_num=retry_num+1,end_time=end_time)
                organic_results=data['organic']

                print(out_link)        
                if 'answerBox' in data :
                    print('answerBox',data['answerBox'])
                    
        
                    if 'answer' in data['answerBox'] and 'title' in data['answerBox']:
                        ans=data['answerBox']['title']+' is '+data['answerBox']['answer']
                        
                        return_ans=return_ans+' . '+ans  
                    if 'snippet' in data['answerBox']:
                        return_ans=return_ans+' . '+data['answerBox']['snippet']  
                    if return_ans=='':
                        https_keys = [key for key, value in data.items() if isinstance(value, str) and re.search(r'https://', value)]
                        filtered_data = {key: value for key, value in data['answerBox'].items() if key not in https_keys}
                        print('直接使用answerbox',filtered_data)
                    print("谷歌问题答案",return_ans)
                    if 'link' in data['answerBox'] :
                            link=data['answerBox']['link']
                            if 'wikipedia.org' in link:
                                out_link=link
                                
                    # else:
                    #     print('answerbox no answer')
                                                    
                    else:
                        if end_time==1:#第二轮不只限于维基百科了
                            link=organic_results[0]['link']
                            return wiki_search(ques,link,retry_num)

                        for inst in organic_results:
                            link=inst['link']
                            if 'wikipedia.org' in link:
                                out_link=link
                                # keyword=inst['title']
                                # return_ans=return_ans+inst['snippet']
                                return_ans=return_ans+scrape_table(link)
                                break        
                else:
                    for inst in organic_results:
                        link=inst['link']
                        if 'wikipedia.org' in link:
                            out_link=link
                            # keyword=inst['title']
                            # return_ans=return_ans+inst['snippet']
                            return_ans=return_ans+scrape_table(link)
                            break        
                cache_instance={googleques:out_link}
                google_cache.update(cache_instance) #更新cache文件               
                if return_ans=='':
                    print("outlink",out_link)
                    if out_link=='':
                        return google_search2(googleques=googleques,ques=ques,retry_num=retry_num+1,end_time=end_time)
                    print('return_ans is empty')
                    return wiki_search(ques=ques,link=out_link,retry_num=retry_num)#几乎不可能走的道路，代表当前没有任何候选项满足条件,所以更换检索器
                
                return_ans=return_ans+' . '
                print('谷歌搜索返回的最终结果',return_ans)
                return return_ans
                # print(data['items'][0]['link'])
            else:
                print("请求失败，状态码:", response.status_code)   
                return 'No result#^'
        except Exception as e:
            print("发生网络错误:", e)
            sendemail(message=str(e),subject='发生网络错误')
            time.sleep(20)
            search_ques=ques
            if retry_num>1:
                # find1=find_prompt+ques+'\n'+"##output: "
                # ques=multichat(find1)
                # topic=wikipedia.search(ques)
                return wiki_search2(search_ques,retry_num=retry_num)
            return google_search2(google_ques,ques,retry_num=retry_num+1,end_time=end_time)        
    else:            
            if googleques not in google_cache:#很少会出现这种情况
                print("缓存中没有找到")
                print("googlecache",google_cache)
                return "empty list"#重新生成问题
            str1=google_cache[googleques]
            if str1=='':
                print("缓存中为空，采用传统方案")
                if end_time==0:
                    return wiki_search2(ques,retry_num=retry_num-1)#初始使用维基百科搜索时，值应该是0
                else:
                    return dpr_search(ques,'',retry_num=retry_num-1)
            if end_time==0:
                return wiki_search(ques,str1,retry_num=retry_num-1)
            else:
                return dpr_search(ques,str1,retry_num=retry_num-1)
            

#%%        
def split_sentence(sentence):
    words = sentence.split()  # 按空格分割句子为单词列表
    if len(words) <= 100:
        return [sentence]  # 如果单词数不超过100，直接返回原句子
    else:
        # 如果单词数超过100，按每100个单词进行拆分
        return [' '.join(words[i:i+100]) for i in range(0, len(words), 100)]
def wiki_search(ques,link,retry_num=0):#问题和修改次数 此为带关键词的维基搜索
    sear_ques=ques
    global find_prompt
    content=''
    know_graph=''
    # try:
    #     parts = ques.split('of', 1)#完成对于问题的分解
    #     # if len(parts)==1:
    #     #     return "No result"
    #     ques=parts[1]
    #     ques = ques.replace('?', '').strip()
    # except Exception:
    #     #无法规则的找到主语
    #     find1=find_prompt+ques+'\n'+"\noutput: "
    #     ques=multichat(find1)
    if retry_num>=2:
    # 无法规则的找到主语
        find1=find_prompt+ques+'\n'+"##output: "
        sentence=[]
        content=''
        break_flag=False
        max_num=0
        ques=''
        for temp_num in range(0,3):
            if break_flag:
                break
            sentence=[]
            ques=multichat(find1)
            print("开始使用网页维基百科辅助检索,检索词为",ques)
            global lasttime
            global ret_tokenizer
            global ret_model
            random_float = random.uniform(5, 7)
            if time.time()-lasttime<random_float:
                time.sleep(random_float-time.time()+lasttime)
            wikipedia.set_lang("en")
            try:
                topic=wikipedia.search(ques)
                    
            except Exception as e:
                print("维基百科搜索失败",e)
                return 'No result#^'
            print(topic)
            
            
            sentence.append(sear_ques)
            lasttime=time.time()
            if (len(topic)==0):
                if(temp_num==2):
                    return "empty list"
                print("空列表")
                continue#重新获取检索词
                
            max_similarity=-999
            
            for i in range(0,len(topic)):
                if ques.strip().lower() == topic[i].lower() or ques.strip().lower()+' (' in topic[i].lower():
                    max_num=i
                    max_similarity=1
                    break
                similarity = ratio(sear_ques.lower(),re.sub(r'\(.*?\)', '', topic[i].lower()) )
                # print(similarity)
                if similarity>max_similarity:
                    max_similarity=similarity
                    max_num=i
            
            
            try:
                print(max_num)
                if max_similarity<0.3:
                    print("相似度过低")
                    content=''
                    continue
                content = wikipedia.page(topic[max_num],auto_suggest=False).content
                link=wikipedia.page(topic[max_num],auto_suggest=False).url
                # print("维基百科链接",link)
                know_graph=scrape_table(link)
                break_flag=True
                break
            except Exception  as e:
                print(e)
    else:            
        print("开始使用网页维基百科辅助检索,网址为",link)
        know_graph=scrape_table(link)
        response = requests.get(link)
        soup = BeautifulSoup(response.text, 'html.parser')
        content = soup.get_text()
        
        # content = wikipedia.page(keyword,auto_suggest=False).content                    
    sentence=[]
    sentence.append(sear_ques)
    print("检索的子问题是",ques)
            # page=page.content.split('.')
            # content=page.content
    if content=='':#找到的主体相似度太低
        print("找到的主体相似度太低或有很多子集")
        return "google#"+ques 
    parts= content.split('.')   #先按照句号进行分组，再重组成400个字以上的句子
    combined_parts = []
    current_part = ""
    for part in parts:
        if len(current_part) + len(part) > 400:
            current_part=split_sentence(current_part)
            combined_parts.extend(current_part)
            current_part = part
        else:
            
            current_part += part
    if current_part:
        current_part=split_sentence(current_part)
        combined_parts.extend(current_part)
    parts = combined_parts
    # parts = [content[i:i+200] for i in range(0, len(content), 200)]
    # parts = content.split('.')
    sentence.extend(parts)
   # embeddings=[]
    # inputs1 = ret_tokenizer(sentence[0], padding=True, truncation=True, return_tensors="pt")
    # inputs1=inputs1.to('cuda:0')
    # embeddings1 = ret_model(**inputs1).squeeze()
    embeddings1=receive(sentence[0])
    # embeddings.append(embeddings1)
    sentence_sort = []
    for i in range(1,len(sentence)):
        
        
        # inputs = ret_tokenizer(sentence[i], padding=True, truncation=True, return_tensors="pt")
        # # inputs=inputs.to('cuda:0')
        # embeddings2 = ret_model(**inputs).squeeze()
        embeddings2=receive(sentence[i])
        # embeddings.append(embeddings2)
        
        score=(embeddings1@embeddings2).item()
        sentence_sort.append({'score':score,'content':sentence[i]})
    sentence_sort.sort(key=lambda x:x['score'],reverse=True)
    # if retry_num>(len(sentence)-1)/2:#重试次数过多
    if retry_num>4 or retry_num>=len(sentence_sort):#重试次数过多
        print("重试次数过多")
        return "No result#"+ques
    # if retry_num==0:#第一次去检索
    ret_ans=''
    if retry_num<2:#第0,一次去检索
        ret_ans=ret_ans+know_graph
    if sentence_sort[retry_num]['content']==sentence[1]:#        
        print("检索到的内容",ret_ans+'\n'+sentence[1])        
        return ret_ans+'\n'+sentence[1]+'.'
    else:#第一段话认为是比较重要的，所以添加上
        print("检索到的内容",ret_ans+'\n'+sentence[1]+'.\n'+sentence_sort[retry_num]['content']+'.')        
        return ret_ans+'\n'+sentence[1]+'\n'+sentence_sort[retry_num]['content']+'.'

def wiki_search2_online(ques,retry_num=0,end_time=0):#问题和修改次数 此为不带关键词的维基搜素
    sear_ques=ques#保存原问题
    print("开始使用网页维基百科辅助检,传入问题为",ques)
    global find_prompt
    if end_time>0 :
        return  dpr_search(ques,'',retry_num=retry_num)
    content=''
    # try:
    #     parts = ques.split('of', 1)#完成对于问题的分解
    #     # if len(parts)==1:
    #     #     return "No result"
    #     ques=parts[1]
    #     ques = ques.replace('?', '').strip()
    # except Exception:
    #     #无法规则的找到主语
    #     find1=find_prompt+ques+'\n'+"\noutput: "
    #     ques=multichat(find1)
    
    # 无法规则的找到主语
    find1=find_prompt+ques+'\n'+"##output: "
    sentence=[]
    content=''
    break_flag=False
    max_num=0
    ques=''
    know_graph=''
    for temp_num in range(0,3):
        if break_flag:
            break
        sentence=[]
        ques=multichat(find1)
        ques_parts = ques.split("is:", 1)
        if(len(ques_parts)>1):
            ques=ques_parts[1]
        print("开始使用网页维基百科辅助检索,检索词为",ques)
        global lasttime
        global ret_tokenizer
        global ret_model
        random_float = random.uniform(5, 7)
        if time.time()-lasttime<random_float:
            time.sleep(random_float-time.time()+lasttime)
        wikipedia.set_lang("en")
        try:
            topic=wikipedia.search(ques)
            
        except Exception as e:
            print("维基百科搜索失败",e)
            return 'No result#^'
        
        
        
        sentence.append(sear_ques)
        lasttime=time.time()
        if (len(topic)==0):
            if(temp_num==2):
                return "empty list"
            print("空列表")
            continue#重新获取检索词
            
        max_similarity=-999
        sim=[]
        for i in range(0,len(topic)):
            if ques.strip().lower() == topic[i].lower() or ques.strip().lower()+' (' in topic[i].lower():

                max_num=i
                max_similarity=2
                sim.append(2)
                continue
            similarity = ratio(sear_ques.lower(), re.sub(r'\(.*?\)', '', topic[i].lower()))
            # print(similarity)
            sim.append(similarity)
            if similarity>max_similarity:
                max_similarity=similarity
                max_num=i
        if max_similarity==2:#存在完全子集的特殊情况
            temp=[]
            for tt in range(0,len(sim)):
                if sim[tt]==2:
                    temp.append((topic[tt],tt))#将所有包含的情况全部找出来
            max_num=temp[0][1] #第一个完全相同的字符        
            if(len(temp)>1):
                print("存在多个完全子集")
                if retry_num==0:
                    content=''
                    break
            if (3<len(temp)-1 and retry_num==3):#3是个超参,到此更换小池子
                max_num=temp[retry_num-2][1]+1   #更换小池子,
        else:
            if retry_num==3:
                if max_num==0:#只变换一次池子
                    max_num=1
                else:
                    max_num=0    
        try:
            print(max_num)
            if max_similarity<0.3:
                print("相似度过低")
                content=''
                continue
            # link=wikipedia.page(topic[max_num],auto_suggest=False).url
            # print("维基百科链接",link)
            know_graph=scrape_table_outline(topic[max_num])
            print("知识小窗",know_graph)
            # print(link)
            # print(link.url)
            content = wikipedia.page(topic[max_num],auto_suggest=False).content
            break_flag=True
            break
        except Exception  as e:
            print(e)


                   
    sentence=[]
    sentence.append(sear_ques)
            # page=page.content.split('.')
            # content=page.content
    if content=='':#找到的主体相似度太低
        print("找到的主体相似度太低或有很多子集")
        return "google#"+ques 
    parts= content.split('.')   #先按照句号进行分组，再重组成200个字以上的句子
    combined_parts = []
    current_part = ""
    for part in parts:
        if len(current_part) + len(part) > 400:
            current_part=split_sentence(current_part)
            combined_parts.extend(current_part)
            current_part = part
        else:
            
            current_part += part
    if current_part:
        current_part=split_sentence(current_part)
        combined_parts.extend(current_part)
    parts = combined_parts
    # parts = [content[i:i+200] for i in range(0, len(content), 200)]
    # parts = content.split('.')
    sentence.extend(parts)
    # embeddings=[]
    # inputs1 = ret_tokenizer(sentence[0], padding=True, truncation=True, return_tensors="pt")
    # inputs1=inputs1.to('cuda:0')
    # embeddings1 = ret_model(**inputs1).squeeze()
    embeddings1=receive(sentence[0])
    # embeddings.append(embeddings1)
    sentence_sort = []
    for i in range(1,len(sentence)):
        
        
        # inputs = ret_tokenizer(sentence[i], padding=True, truncation=True, return_tensors="pt")
        # # inputs=inputs.to('cuda:0')
        # embeddings2 = ret_model(**inputs).squeeze()
        embeddings2=receive(sentence[i])
        # embeddings.append(embeddings2)
        
        score=(embeddings1@embeddings2).item()
        sentence_sort.append({'score':score,'content':sentence[i]})
    sentence_sort.sort(key=lambda x:x['score'],reverse=True)
    # if retry_num>(len(sentence)-1)/2:#重试次数过多
    if retry_num>4  or retry_num>=len(sentence_sort):#重试次数过多
        print("重试次数过多")
        return "No result#"+ques
    ret_ans=''
    if retry_num<2:#第0,一次去检索
        ret_ans=ret_ans+know_graph
    if sentence_sort[retry_num]['content']==sentence[1]:#        
        print("检索到的内容",ret_ans+'\n'+sentence[1])        
        return ret_ans+'\n'+sentence[1]+'.'
    else:#第一段话认为是比较重要的，所以添加上
        print("检索到的内容",ret_ans+'\n'+sentence[1]+'.\n'+sentence_sort[retry_num]['content']+'.')        
        return ret_ans+'\n'+sentence[1]+'\n'+sentence_sort[retry_num]['content']+'.'
def wiki_search2(ques,retry_num=0,end_time=0):#问题和修改次数 此为不带关键词的维基搜素
    sear_ques=ques#保存原问题
    global find_prompt
    if end_time>0 :
        return  dpr_search(ques,'',retry_num=retry_num)
    content=''
    # try:
    #     parts = ques.split('of', 1)#完成对于问题的分解
    #     # if len(parts)==1:
    #     #     return "No result"
    #     ques=parts[1]
    #     ques = ques.replace('?', '').strip()
    # except Exception:
    #     #无法规则的找到主语
    #     find1=find_prompt+ques+'\n'+"\noutput: "
    #     ques=multichat(find1)
    
    # 无法规则的找到主语
    find1=find_prompt+ques+'\n'+"##output: "
    sentence=[]
    content=''
    
    max_num=0
    ques=''
    know_graph=''
  
    sentence=[]
    ques=ques=multichat(find1)#之后的所有ques都是主体名
    if ques.strip()=='':
        print(find1)
        ques=ques=multichat(find1)
        ques_parts = ques.split("is:", 1)
        if(len(ques_parts)>1):
            ques=ques_parts[1]
    print("开始使用维基百科2辅助检索,检索词为",ques)
    global ret_tokenizer
    global ret_model

    retriever = BM25_1(
        tokenizer=prompt_tokenizer,
        index_name='wiki1',
        engine='elasticsearch',
        exclude_domains=['wikipedia.org', 'wikiwand.com', 'wiki2.org', 'wikimedia.org'])
    ans=retriever.retrieve([ques], topk=20)[1][0]
    # print(ans)
    topic=[]
    try:
        for tt in range(0,len(ans)):
            topic.append(ans[tt]['title'])
    except Exception as e:
        print(e)
        print("wiki错误,ans为",ans)


   
    
    
    sentence.append(sear_ques)
   
        
    max_similarity=-999
    sim=[]#子集的所有情况
    for i in range(0,len(topic)):
        if ques.strip().lower() == topic[i].lower() or ques.strip().lower()+' (' in topic[i].lower():

            max_num=i
            max_similarity=2
            sim.append(2)
            continue
        similarity = ratio(sear_ques.lower(),re.sub(r'\(.*?\)', '', topic[i].lower()) )#去除括号的内容再去计算相似度
        # print(similarity)
        sim.append(similarity)
        if similarity>max_similarity:
            max_similarity=similarity
            max_num=i
    if max_similarity==2:#存在完全子集的特殊情况
        temp=[]
        for tt in range(0,len(sim)):
            if sim[tt]==2:
                temp.append((topic[tt],tt))#将所有包含的情况全部找出来
        max_num=temp[0][1] #第一个完全相同的字符        
        if(len(temp)>1):
            print("存在多个完全子集")
            return "google#"+ques 
                
        if (3<len(temp)-1 and retry_num==3):#3是个超参,到此更换小池子
            max_num=temp[retry_num-2][1]+1   #更换小池子,
    else:
        if retry_num==3:
            if max_num==0:#只变换一次池子
                max_num=1
            else:
                max_num=0    

    
    
    
    print(max_num)
    if max_similarity<0.8:
        print("相关性太低")
        return "google#"+ques 
    title=topic[max_num]
    
    # print("维基百科链接",link)
    # know_graph=scrape_table(link)
    know_graph=scrape_table_outline(topic[max_num])
    print("知识小窗",know_graph)
    # print(link)
    # print(link.url)
    content = ''
    for tt in range(0,len(ans)):
        if ans[tt]['title']==title:
            content=ans[tt]['text']
            break
        
   


                   
    sentence=[]
    sentence.append(sear_ques)
            # page=page.content.split('.')
            # content=page.content
    if content=='':#找到的主体相似度太低
        print("找到的主体相似度太低或有很多子集wiki2")
        return "google#"+ques 
    parts= content.split('.')   #先按照句号进行分组，再重组成200个字以上的句子
    combined_parts = []
    current_part = ""
    for part in parts:
        if len(current_part) + len(part) > 400:
            current_part=split_sentence(current_part)
            combined_parts.extend(current_part)
            current_part = part
        else:
            
            current_part += part
    if current_part:
        current_part=split_sentence(current_part)
        combined_parts.extend(current_part)
    parts = combined_parts
    # parts = [content[i:i+200] for i in range(0, len(content), 200)]
    # parts = content.split('.')
    sentence.extend(parts)
    # embeddings=[]
    # inputs1 = ret_tokenizer(sentence[0], padding=True, truncation=True, return_tensors="pt")
    # inputs1=inputs1.to('cuda:0')
    # embeddings1 = ret_model(**inputs1).squeeze()
    embeddings1=receive(sentence[0])
    # embeddings.append(embeddings1)
    sentence_sort = []
    for i in range(1,len(sentence)):
        
        
        # inputs = ret_tokenizer(sentence[i], padding=True, truncation=True, return_tensors="pt")
        # # inputs=inputs.to('cuda:0')
        # embeddings2 = ret_model(**inputs).squeeze()
        embeddings2=receive(sentence[i])
        # embeddings.append(embeddings2)
        
        score=(embeddings1@embeddings2).item()
        sentence_sort.append({'score':score,'content':sentence[i]})
    sentence_sort.sort(key=lambda x:x['score'],reverse=True)
    # if retry_num>(len(sentence)-1)/2:#重试次数过多
    if retry_num>4  or retry_num>=len(sentence_sort):#重试次数过多
        print("重试次数过多")
        return "No result#"+ques
    ret_ans=''
    if retry_num<2:#第0,一次去检索
        ret_ans=ret_ans+know_graph
    if sentence_sort[retry_num]['content']==sentence[1]:#        
        print("检索到的内容",ret_ans+'\n'+sentence[1])        
        return ret_ans+'\n'+sentence[1]+'.'
    else:#第一段话认为是比较重要的，所以添加上
        print("检索到的内容",ret_ans+'\n'+sentence[1]+'.\n'+sentence_sort[retry_num]['content']+'.')        
        return ret_ans+'\n'+sentence[1]+'\n'+sentence_sort[retry_num]['content']+'.'


def dpr_search(message,keyword='',retry_num=1):#传统密集减速器方案
    host = '219.216.64.107'
    print("开始使用密集检索器dpr")
    port = 12345
    # if keyword=='':
    #     find1=find_prompt+ques+'\n'+"##output: "
    #     keyword=multichat(find1)
    if retry_num>1:
        return eles_search(message,retry_num=retry_num)#后续替换为稀疏检索器
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, port))
        except socket.error as msg:
            print(msg)
     
        # while True:
        # print('Sending', message)
        s.sendall(message.encode())
        data = s.recv(1024*1024)
        
        # print('Received', data.decode())
        res=str(data.decode())
        list_data = json.loads(res)
        # print('Received', list_data[0])
        s.close()
        if type(list_data)!=str:
            list_data = ' '.join(map(str, list_data))
        print("密集检索器返回的结果",list_data)    
        return list_data
prompt_tokenizer = GPT2TokenizerFast.from_pretrained('gpt2')
prompt_tokenizer.pad_token = prompt_tokenizer.eos_token

def eles_search(ques,retry_num=0):#使用稀疏减速器进行检索
    if retry_num>2:
        return 'No result#^'#此为全部终止，停止全部回溯
    print("开始使用稀疏检索器elas")
    retriever = BM25(
        tokenizer=prompt_tokenizer,
        index_name='wikipedia_dpr',
        engine='elasticsearch',
        exclude_domains=['wikipedia.org', 'wikiwand.com', 'wiki2.org', 'wikimedia.org'])
    ans=retriever.retrieve([ques], topk=1)
    if len(ans)<2:
        print("稀疏检索器出现问题")
        print(ans)
        return eles_search(ques,retry_num=retry_num+1)
    print("稀疏检索器返回的结果",ans[1][0][0])
    return json.dumps(ans[1][0][0])                        
# response = requests.get(url, headers=headers)

# def search(message):
    # host = 'localhost'
    # port = 12348

    # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    #     try:
    #         s.connect((host, port))
    #     except socket.error as msg:
    #         print(msg)
     
    #     # while True:
       

    #     # print('Sending', message)
    #     s.sendall(message.encode())
    #     data = s.recv(1024*1024)
        
    #     # print('Received', data.decode())
    #     res=str(data.decode())
    #     list_data = json.loads(res)
    #     # print('Received', list_data[0])
    #     s.close()
    #     return list_data


def multichat2(message):#较难的问题,此处后续使用大参数模型进行计算
    # return multichat(message)
    return chatgpt3(0,message)
    response, history = parallel_model_4.chat(tokenizer, message, history=[])
    return response
    # host = 'localhost'
    # port = 12348

    # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    #     try:
    #         s.connect((host, port))
    #     except socket.error as msg:
    #         print(msg)
     
    #     # while True:
       

    #     # print('Sending', message)
    #     s.sendall(message.encode())
    #     data = s.recv(1024*1024)
        
    #     # print('Received', data.decode())
    #     res=str(data.decode())
    #     list_data = json.loads(res)
    #     print(list_data)
    #     print('Received', list_data[0])
    #     s.close()
    #     return list_data
# def multichat(message):
#     if time.time()-gemini_lastime<2:
#         time.sleep(2)
#     gemini_model = genai.GenerativeModel('gemini-pro')
#     response = gemini_model.generate_content(message)
#     return response.text
   

# def multichat1(message):
#     # response, history = model2.chat(tokenizer2, message, history=[])   
#     # return response 
#     messages=[
#             {
#                 "role": "user",
#                 "content": message,
#             }        ]
#     encodeds = tokenizer2.apply_chat_template(messages, return_tensors="pt")
#     model_inputs = encodeds.to(device1)
    
#     generated_ids = model2.generate(model_inputs, max_new_tokens=400, do_sample=True)
#     decoded = tokenizer2.batch_decode(generated_ids)
#     print(decoded[0])
#     model_inputs = encodeds.cpu()
#     return decoded[0]
def find_first_with_substring(lst, substring):
    return next((s for s in lst if substring in s), None)
def SCmultichat2(message,times,question):#子问题SC对齐,采用大模型进行回答,所以信任
    for SCtime in range(0,times):
        response=multichat2(message)
        response=str(response)
        # print("未提取子问题的答案",response)
        for exact_num in range(0,2):#未按照COT格式输出，重新生成
            if ('Analyzing' in response or 'Analyze' in response)and 'Known Information' in response and 'Answer' in response:
                break
            print("生成格式不对")
            response=multichat2(message)
            response=str(response)
            # print("未提取子问题的答案",response)
        response=exact_answer(response)
        # temp_list=re.findall(r'\b\d{4}\b', response)
        # if (len(temp_list)>0):
        #     year_num=year_num+1
        #     year=temp_list[0]
        # print("子问题的答案",response)
        keyword=exact_answer2(response,ques)
        print("关键词",keyword)
        keyword_list.append(keyword)
        response_list.append(response)  
    most_common_word, most_common_count = Counter(keyword_list).most_common(1)[0]
    position = keyword_list.index(most_common_word)
    response=response_list[position]
    return response,most_common_word  
def SCmultichat(message,times,question):#子问题SC对齐
    keyword_list=[]
    response_list=[]
    d = dict()
    for SCtime in range(0,3):
        
        response=multichat(message)
        # print("未提取的子问题答案",response)
        response=str(response)
        for exact_num in range(0,2):#未按照COT格式输出，重新生成
            if ('Analyzing' in response or 'Analyze' in response)and 'Known Information' in response and 'Answer' in response:
                break
            print("生成格式不对")
            response=multichat(message)
            response=str(response)
            # print("未提取子问题的答案",response)
        # print("未提取原问题的答案",response)
        response=exact_answer(response)
        # print("子问题问题的答案",response)
        keyword=multichat(exact_prompt2+response+"\n##question:"+question+'\n'+"##output:") 
        print("子问题关键词",keyword) 
        keyword_list.append(keyword)
        response_list.append(response)
        d[keyword] = d.setdefault(keyword, 0) + 1
        
        # setdefault()函数,如果键不存在于字典中，将会添加键并将值设为默认值
    most_common_word = Counter(keyword_list).most_common(1)[0][0]        
    if d[most_common_word]<2:
        for SCtime in range(0,3):
        
            response=multichat(message)
            # print("未提取的子问题答案",response)
            response=str(response)
            for exact_num in range(0,2):#未按照COT格式输出，重新生成
                if ('Analyzing' in response or 'Analyze' in response)and 'Known Information' in response and 'Answer' in response:
                    break
                print("生成格式不对")
                response=multichat(message)
                response=str(response)
                # print("未提取子问题的答案",response)
            # print("未提取原问题的答案",response)
            response=exact_answer(response)
            print("子问题问题的答案",response)
            keyword=multichat(exact_prompt2+response+"\n##question:"+question+'\n'+"##output:") 
            print("子问题关键词",keyword) 
            keyword_list.append(keyword)
            response_list.append(response)
            d[keyword] = d.setdefault(keyword, 0) + 1

    most_common_word = Counter(keyword_list).most_common(1)[0][0]

            # 找出这个单词在列表中的位置
    position = keyword_list.index(most_common_word)

    response=response_list[position]
    print("最终子问题答案",response)
    print("最终子问题关键词",most_common_word)
    return response,most_common_word
# def SCmultichat(message,times,question):#子问题SC对齐
#     if times>=20:#当前模型无法解决
#         print("times 过多")
#         return "not",'not'#超过20次,代表不知道该问题的答案
    
    
#     threads=[]
#     response=''
#     global year 
#     global year_num

#     # for SCtime in range(0,times):
#     #     response=multichat(message)
#     #     response=str(response)
#     #     # print("未提取子问题的答案",response)
#     #     for exact_num in range(0,3):#未按照COT格式输出，重新生成
#     #         if ('Analyzing' in response or 'Analyze' in response)and 'Known Information' in response and 'Answer' in response:
#     #             break
#     #         print("生成格式不对")
#     #         response=multichat(message)
#     #         response=str(response)
#     #         # print("未提取子问题的答案",response)
#     #     response=exact_answer(response)
#     #     temp_list=re.findall(r'\b\d{4}\b', response)
#     #     if (len(temp_list)>0):
#     #         year_num=year_num+1
#     #         year=temp_list[0]
#     #     # print("子问题的答案",response)
#     #     keyword=exact_answer2(response,ques)
#     #     print("关键词",keyword)
#     #     keyword_list.append(keyword)
#     #     response_list.append(response)
#     temp_key_word_list=[]
#     temp_response_list=[]
#     for SCtime in range(0,times):
#         if SCtime%5==0 and SCtime!=0:
#             for t in threads:
#                 t.join()
#             threads.clear()
#             temp_key_word_list.extend(keyword_list)
#             temp_response_list.extend(response_list)
#         t = threading.Thread(target=parallel_chat, args=(message,question,SCtime%5))        
#         t.start()
#         threads.append(t)
#     for t in threads:
#         t.join()
#     threads.clear()
#     temp_key_word_list.extend(keyword_list)
#     temp_response_list.extend(response_list)
#     threads.clear()
#     print("长度",len(temp_key_word_list))
#     most_common_word, most_common_count = Counter(temp_key_word_list).most_common(1)[0]
#     position = temp_key_word_list.index(most_common_word)
#     response=temp_response_list[position]
#     if 'date' in question and times==10 :##询问时间并且经过了一轮搜索
#         first_with_substring = find_first_with_substring(temp_key_word_list, str(year))
#         if year_num>5:
#             print("年份",year)
#             return first_with_substring,year
#         else:
#             print("年份不明显")
#             return "not",'not'

#     if times>=10:
#         print("回溯次数过多")#关键词明显
       
#         print("最终子问题答案",response)
#         print("最终子问题关键词",most_common_word)
#         return response,most_common_word
#     if most_common_count<times/2+1:
#         print("关键词不明显")
#         return SCmultichat(message,times*2,question)
#     if ' no ' in response or'not' in response or'sorry' in response or 'Unfortunately' in response:#错误
#         return response,most_common_word
    
#     if re.search(r'\d{4}', most_common_word)!=None:
#         print("关键词为年份")
#         print("最终子问题答案",response)
#         print("最终子问题关键词",most_common_word)
#         return response,most_common_word


#     if most_common_word not in message:
#         print("关键词不在问题中",most_common_word)
#         return SCmultichat(message,times*2,question)
#     if 'date' in question:
#         print("最终子问题答案",response)
#         print("最终子问题关键词",most_common_word)
#         return response,most_common_word
#     # 找出这个单词在列表中的位置,防止出现关键字不全的情况
#     position1 = message.find(most_common_word)
#     if position1>=1:
#         char_before = message[position1 - 1]
#         if char_before.isalpha():
#             print("关键词前有字母")
#             return SCmultichat(message,times*2,question)
#     end = position1 + len(most_common_word)
#     if end < len(message):
#         char_after = message[end]
#         print()
#         if char_after.isalpha():
#             print("关键词后有字母",char_after)
#             return SCmultichat(message,times*2,question)
    
#     print("最终子问题答案",response)
#     print("最终子问题关键词",most_common_word)
#     return response,most_common_word
def loadfile(path):
    with open(path, 'r') as f:
        data = json.load(f)
    return data

# tokenizer = AutoTokenizer.from_pretrained("/data/zhangxiaoming/personal/fenjiechatglm", trust_remote_code=True, device=device)
# model = AutoModel.from_pretrained("/data/zhangxiaoming/personal/fenjiechatglm", trust_remote_code=True, device=device)
# model = model.eval()
# response, history = model.chat(tokenizer, "你好", history=[])
# print(response)
ret_tokenizer = AutoTokenizer.from_pretrained('facebook/contriever-msmarco')
ret_model = Contriever.from_pretrained("facebook/contriever-msmarco").to('cuda')  
#%%
def cot_sc(question):
    try:
        d = dict()
        for SCtime in range(0,3):
            ans1=question+"Let's think this question step by step!"
            # print(ans1)
            response=multichat(question+"Let's think this question step by step!")
            print("当前为过滤后的答案",response)
            response=str(response)
            # for exact_num in range(0,2):#未按照COT格式输出，重新生成
            #     if ('Analyzing' in response or 'Analyze' in response)and 'Known Information' in response and 'Answer' in response:
            #        break
            #     print("生成格式不对")
            #     response=multichat(ans1)
            #     response=str(response)
            #     # print("未提取子问题的答案",response)
            # # print("未提取原问题的答案",response)
            # response=exact_answer(response)
            print("问题的答案",response)
            keyword=exact_answer4(response,question)
            print("关键词",keyword) 
            keyword_list.append(keyword)
            response_list.append(response)
            d[keyword] = d.setdefault(keyword, 0) + 1
            
            # setdefault()函数,如果键不存在于字典中，将会添加键并将值设为默认值
        most_common_word = Counter(keyword_list).most_common(1)[0][0]        
        if d[most_common_word]<2:
            for SCtime in range(0,4):
                ans1=question+"Let's think this question step by step!"
                # print(ans1)
                response=multichat(ans1)
                print("当前为过滤后的答案",response)
                response=str(response)
                # for exact_num in range(0,2):#未按照COT格式输出，重新生成
                #     if ('Analyzing' in response or 'Analyze' in response)and 'Known Information' in response and 'Answer' in response:
                #         break
                #     print("生成格式不对")
                #     response=multichat(ans1)
                #     response=str(response)
                #     # print("未提取子问题的答案",response)
                # # print("未提取原问题的答案",response)
                # response=exact_answer(response)
                print("问题的答案",response)
                keyword=exact_answer4(response,question)
                print("关键词",keyword) 
                keyword_list.append(keyword)
                response_list.append(response)
                d[keyword] = d.setdefault(keyword, 0) + 1
        # ans1=ans_prompt+question+'\n'+'##konwn information:'+known_info+'\n'+'##output:'
        # response=multichat(ans1)
        # print("当前轮次为过滤的答案",response)
        # response=multichat_three(ans1,response,'So, answer me in the form of "The answer is:"')
        
        # print("问题的答案",response)
        print("正确的答案",answer)
        print("问题是",question)
        most_common_word = Counter(keyword_list).most_common(1)[0][0]

            # 找出这个单词在列表中的位置
        position = keyword_list.index(most_common_word)

        response=response_list[position]
        print("回复",response)
        print("最终答案",response)
        

        print("最终keyword",most_common_word)
        return response,most_common_word
        # temp_ans=can_answer(response,question)
        # print("是否能回答",temp_ans)#LLM 判断不准确，当做第二道保险
        # if 'yes' in temp_ans:
        #     response=response_list[position]
        # else:      
#Based on the known information, the director of the film "The Half-Way Girl," John Francis Dillon, was born in New York, New York.
        #     if 'no' in response or 'not' in response or 'sorry' in response or 'Unfortunately' in response:
        #         response=multichat(question)
        #         most_common_word=exact_answer3(response,question,'')
        
    except Exception as e:
        ans1=question+"Let's think this question step by step!"
            # print(ans1)
        response=multichat(question+"Let's think this question step by step!")
        most_common_word=exact_answer4(response,question)
        return response,most_common_word
api_key=['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','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','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']
proxy=['http://127.0.0.1:10101','http://127.0.0.1:10102','http://127.0.0.1:10103']
api_num=0
# def qwenchat(message):
#     # print("GPT3.5开始回答",message)
#     num123=0
          
        
#     while num123<10:
#         try:
#             global apinum1
#             apinum1=(apinum1+1)%2
#             acquire_lock()
#             chat_completion = client2[apinum1].chat.completions.create(
#                 messages=message,
#             stream=False,
#                 model="llama-3-70b")
#             # release_lock()
#             # time.sleep(0.5)
#             # print("GPT3.5回答",chat_completion.choices[0].text)
#             return chat_completion.choices[0].message.content
#         except Exception as e:
#             print(e)
#             print(apinum1)
#             num123=num123+1
#             time.sleep(random.randint(10,30))
#     global endtimes1
#     sendemail(message=str(1),subject='第'+str(endtimes1)+'次试图修复')
#     if(endtimes1<20):
#         t=endtimes1
#         time.sleep(random.randint(500,700))
#         endtimes1=t+1
#         return multichat(message)
#     exit()
def qwenchat(message):
    # print("GPT3.5开始回答",message)
    client9=[OpenAI(
    api_key="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",
    base_url="http://159.89.238.3:22821/api.groq.com/openai/v1",
)]
    num123=0
          
        
    while num123<10:
        try:
            global apinum1
            apinum1=(apinum1+1)%2
            # acquire_lock()
            chat_completion = client9[0].chat.completions.create(
                messages=message,
            stream=False,
                model="llama3-70b-8192")
            # release_lock()
            # time.sleep(0.5)
            # print("GPT3.5回答",chat_completion.choices[0].text)
            return chat_completion.choices[0].message.content
        except Exception as e:
            print(e)
            print(apinum1)
            num123=num123+1
            time.sleep(random.randint(10,30))
    global endtimes1
    sendemail(message=str(1),subject='第'+str(endtimes1)+'次试图修复')
    if(endtimes1<20):
        t=endtimes1
        time.sleep(random.randint(500,700))
        endtimes1=t+1
        return multichat(message)
    exit()
# def qwenchat(message):
#     num123=0
#     while num123<10:
#         try:
#             global api_num
            
#             global apinum1
#             apinum1=(apinum1+1)%6
            
#             chat_completion = client2[0].chat.completions.create(
#                 messages=message,
#                 model="llama3-70b-8192")
#             api_num=(api_num+1)%3
#             return chat_completion.choices[0].message.content
            
#         except Exception as e:
#             print(e)
#             time.sleep(10)
#             print(apinum1)
#             num123=num123+1
#             # sendemail(message=str(e),subject='GPT3.5错误')
#             api_num=(api_num+1)%3
#     sendemail('error','error')
#     exit()
def confirm_ques(message):
    ques=qwenchat(message)
    ques_list=[]


    ques_list.append(ques)
    print("分解后的子问题",ques)
    for iii in range(0, 5):
        ques=qwenchat(message)
        
        ques_list.append(ques)
    similarities = [ratio(ques_list[i].lower(), ques_list[j].lower()) for i in range(len(ques_list)) for j in range(i+1, len(ques_list))]
    avg_similarity = sum(similarities) / len(similarities)

    print("平均相似度",avg_similarity)
    if avg_similarity>0.9:
        return ques_list[0]
    else:
        return '0'+ques_list[0]#返回0表示问题不合理,之后会再次处理
def make_print_to_file(path='./'):
    '''
    A function to redirect print statements to a log file.

    :param path: The path to the directory where the log file should be saved.
    :return: None
    '''
    import sys
    import os
    import datetime
 
    class Logger(object):
        def __init__(self, filename="Default.log", path="./"):
            '''
            :param filename: The name of the log file to be created.
            :param path: The path to the directory where the log file should be saved.
            '''
            self.terminal = sys.stdout # terminal是标准输出，即print函数输出的位置
            self.path= os.path.join(path, filename) # path是文件保存的路径
            self.log_file = open(self.path, "a", encoding='utf8',) # log_file是文件对象，用于写入文件
            print("Saving logs to:", os.path.join(self.path, filename)) # 打印日志保存的路径
 
        def write(self, message):
            '''
            Writes the message to both the terminal and the log file.

            :param message: The message to be written.
            '''
            self.terminal.write(message) # 将message写入到terminal，即标准输出
            self.log_file.write(message) # 将message写入到log_file，即文件
            self.log_file.flush() # 刷新缓存区，即将缓存区的内容写入到文件(这个地方一定要刷新，不然的话，文件中会没有内容)
 
        def flush(self):
            pass
    file_name = os.path.basename(__file__)
    # Create a new log file with the current date as the filename
    fileName = datetime.datetime.now().strftime('day'+'%Y_%m_%d')+file_name
    sys.stdout = Logger(fileName + '.log', path=path)
 
    # Print a header to indicate that all subsequent print statements will be logged
    print("Logging started for:", fileName.center(60,'*'))

    # Return the logger object
    return sys.stdout.log_file
output=[]
log_file = make_print_to_file(path='./')
data = loadfile('/data/zhangxiaoming/model/dataset/bam.json')
#存储上一轮对话,初始为空
print(len(data))
print(dpr_search('11'))
print(eles_search('11'))
yes=0
#第15个有错误
num1=41+38
num2=len(data)
print("num1",num1)
print("num2",num2)
for i in range(num1,num2):
        torch.cuda.empty_cache()  # 释放显存
        instance = data[i]
        question = instance['question']
        print("问题:",question)
        answer = instance['answer']
        # evidenve = instance['question_decomposition']
        
        cot_prompt1=cot_prompt+'\n'+'question:'+question+'\n'+'konwn information:'
        num=0
        search_flag=False
        # if i==20000:
        #         break
        known_info=[]
        lastquestion=[]
        kind={}#主体的类型
        # matches = re.findall(r'\((.*?)\)', question)#提取括号内的信息
        # matches2 = re.findall(r'(\w+)\s*\(', question)#提取括号前的第一个单词
        # for iii in range(0, len(matches)):
        #     kind[matches2[iii]]=matches[iii]#加入key,value.key为第一个单词,value为括号内的信息
        
        # buffer_instance={'question':'','answer':''}
        # search_ans=str(wiki_search(question))
        # direct_prompt1=direct_prompt+question+'\n##information:'+search_ans+'\n##output:'
        # direct_response=multichat(direct_prompt1)
        # direct_response=str(direct_response)
        times=0# 回溯次数
        cot_messaeges=[]
        cot_messaeges.append({'role':'system','content':cot_prompt})
        cot_messaeges.append({'role':'user','content':"Let's break down this complex question"+question})
        while num<6:
            torch.cuda.empty_cache()  # 释放显存
            print("轮数+1")
            num=num+1
            input=''
            
            print("已知的信息",','.join(known_info))  
            # if buffer_instance['answer']==''or times>0 :#初始状态或者上一轮对话有问题回溯状态
            # can_answer_flag=can_answer1(','.join(known_info),question)
            # print("LLM是否能回答",can_answer_flag)
            # if num>2:
            #     if 'yes' in can_answer_flag:
            #         print("LLM 认为信息足够")
            #         # break
           
            # else:
            #     input=cot_prompt1+known_info+','+buffer_instance['answer']+'\n'+'output:'
            kind={}#暂时不手动添加种类    
            ques=confirm_ques(cot_messaeges)
            print("产生的子问题",ques)
            if(ques.strip()==''):
                ques=confirm_ques(cot_messaeges)
                print("重新产生的子问题",ques)
            if " enough" in ques:
                print("LLM 认为信息足够",ques)
                break
            if ques[0]=='0' and num>4:
                print("问题不合理")
                break
            if ques.startswith("0"):
                ques=ques[1:]
            if ques in lastquestion and times==0:#问题重复且不是回溯的情况
                # known_info=known_info+buffer_instance['answer']+', '
                print("问题重复")
                break
            cot_messaeges.append({'role':'assistant','content':ques})
            find1=find_prompt+ques+'\n'+"##output: "
            temp_find1=multichat(find1)#找到实体
            # if temp_find1 in known_info or temp_find1 in question:
            #     print("子问题正常")
            # else:
            #     revise_prompt1=revise_prompt+'##question:'+question+'\n'+'##konwn information:'+','.join(known_info)+'\n##subquestion:'+ques+'\n##output:'
            #     ques=multichat(revise_prompt1)
            #     print("修正后的子问题",ques)  
            lastquestion.append(ques)
            retry_num=0
            response=''
            add_instance=''
            break_flag=False#是否跳出的标志,两层循环从内部跳出
            times_flag=False #是否回溯的标志
            logit=1.0 #初始默认概率
            while True:
                torch.cuda.empty_cache()  # 释放显存
                if times>1:#回溯两次还找不到对应的答案,直接跳出

                    print("times>1")
                    response=direct_answer(ques_prompt+ques+'\n##output:',ques)
                    temp_ans=can_answer(response,ques)
                    # response=multichat(exact_prompt4+ques+'\n##reply:'+response+'\n##output:')
                    print("LLM回答",response)
                    # temp_ans=can_answer(response,ques)
                    print("是否能回答",temp_ans)#LLM 判断不准确，当做第二道保险
                    if 'yes' in temp_ans:
                            break #继续下一轮问答
                    else:
                        break_flag=True#找不到答案，终止
                        break  
                if retry_num>10:
                    break_flag=True#找不到答案，终止
                    break 
                search_ans=str(wiki_search2(ques,retry_num=retry_num,end_time=times))
                # ques='what is the father of Alexandre Berthier, 3rd Prince of Wagram?'
                # search_ans='twice#'
                print("搜索到的知识",search_ans)
                if retry_num>0:
                    print("重试次数",retry_num)
                if search_ans=='empty list':#找不到相关主体,重新获取子问题
                    # ques=confirm_ques(input,kind)
                    retry_num=retry_num+1
                    if ques[0]=='0' and num>=3:
                        break_flag=True
                        break
                    if ques in lastquestion and times==0:#问题重复且不是回溯的情况
                        break_flag=True
                        break
                    lastquestion.pop()#退出之前的问题
                    lastquestion.append(ques)
                    continue
                if 'twice#' in search_ans:
                    search_ans= str(google_search2(ques,ques,retry_num,times))
                    print("第二轮搜索到的结果",search_ans)
                if 'google#'in search_ans :
                    after_no_result = search_ans.split('google#', 1)[1]
                    print('有太多混淆项,启动谷歌搜索',after_no_result)
                    temp_num=-1#保存包含对应实体的答案
                    for known_info_num in range(0,len(known_info)):
                        if after_no_result in known_info[known_info_num]:
                            temp_num=known_info_num
                            break
                    print("temp_num",temp_num)
                    google_ques=''
                    if 'question:' in ques:
                        google_ques=ques.split('question:', 1)[1]
                    else:    
                        google_ques=ques#子问题
                    if temp_num==-1:#
                        google_ques=google_ques #当前主体在之前的回答中没有找到
                    else:
                        enetity_prompt=google_entity_prompt+'##entity:'+after_no_result+'\n'+'##information:'+known_info[temp_num]+'\n##output:'
                        eneity_temp=multichat(enetity_prompt)
                        print("转化后的描述为:",eneity_temp)
                        search_flag=True

                        google_ques=google_ques+' '+eneity_temp#当前主体在之前的回答中找到    
                    
                    search_ans=google_search2(google_ques,ques,retry_num=retry_num,end_time=times)

                if 'No result#'in search_ans :#上一论对话有问题,此时要起模型重新回答上一轮对话
                    after_no_result = search_ans.split('No result#', 1)[1]
                    print('问题无法解决,进行回溯找到对应答案',after_no_result)
                    temp_num=-1#保存包含对应实体的答案
                    for known_info_num in range(0,len(known_info)):
                        if after_no_result in known_info[known_info_num]:
                            temp_num=known_info_num
                            break
                    print("temp_num",temp_num)  
                    if times==1:#及时退出循环
                        break_flag=True
                        break  
                    # if temp_num==-1:#找不到对应的答案
                        # break_flag=True
                    num=num-1 #第二次尝试搜索
                    lastquestion=lastquestion[:num]
                    known_info=known_info[:num]
                    if 'assistant' in cot_messaeges[-1]['role']:
                        cot_messaeges.pop()
                        # times_flag=True#避免添加信息
                        # break
                    # else:#第二次回溯不要删除问题
                    # # print("找到对应的答案",known_info[temp_num])
                    #     num=temp_num-1
                    #     retry_num=retry_num+1
                    #     lastquestion=lastquestion[:num]
                    #     known_info=known_info[:num]
                    times=times+1
                    times_flag=True
                    break
                add_instance='##question:'+ques+'\n'+"##konwn information:"+search_ans+'\n'+'##output:'
                ret=ret_prompt+add_instance
                # global year
                # global year_num
                year=0
                year_num=0
                response,key_temp=SCmultichat(ret,1,ques)
                key_temp=key_temp.lower()  
                print("最终答案",response)
                print("最终关键词",key_temp)
                key_temp=key_temp.lower()
                temp_ans=can_answer(response,ques)
                print("是否能回答",temp_ans)#LLM 判断不准确，当做第二道保险
                if 'yes' in temp_ans:
                        break
                else:
                    temp_logit= random.randint(1, 100)
                    threshold=(retry_num / 5) ** 2#当前的阈值
                    if temp_logit<threshold*100:#一定概率下进行,随着retry_num增加,概率增加,且增加的一阶导数增强(一阶,二阶导数均大于0)
                        response=direct_answer(ques_prompt+ques+'\n##output:',ques)
                        temp_ans=can_answer(response,ques)
                        # response=multichat(exact_prompt4+ques+'\n##reply:'+response+'\n##output:')
                        print("LLM回答",response)
                        
                        print("是否能回答",temp_ans)#LLM 判断不准确，
                        if 'yes' in temp_ans:#如果能回复，则正常进行
                            break
                retry_num=retry_num+1
        
                continue
                # if 'information need'in key_temp or 'unable'in key_temp or ' no ' in key_temp or'not' in key_temp or'sorry' in key_temp or 'Unfortunately' in key_temp or 'unknown' in key_temp or 'unclear' in key_temp or 'unspecified' in key_temp:#
                    
                #     retry_num=retry_num+1
                #     continue
                
                break
            if break_flag==True: 
                break   
            if times_flag==True:
                continue    
            # if ' no ' in response or'not' in response or'sorry' in response or 'Unfortunately' in response:#
            #     break
            
            #更新buffer结果,
            known_info.append(response)
            cot_messaeges.append({'role':'user','content':response})
            # ans1=ans_prompt+question+'\n'+'##konwn information:'+','.join(known_info)+'\n'+'##output:'
            #计算困惑度
            # input_ids = tokenizer.encode(ans1, return_tensors='pt').to(device)
            # generated_ids = model(input_ids,labels=input_ids)
            # print("当前困惑度为:",generated_ids.loss)
            # response=multichat(ans1)
            # print("当前轮次为过滤的答案",response)
            # response=multichat_three(ans1,response,'So, answer me in the form of "The answer is:"')
            # print("当前轮次问题的答案",response)
            print("当前已知的信息",','.join(known_info))
            # print("正确的答案",answer)    

        keyword_list=[]
        response_list=[]
        d = dict()
        print("知道的信息",','.join(known_info))
        print("问题是",question)
        for SCtime in range(0,3):
            ans1=ans_prompt+question+'\n'+'##konwn information:'+','.join(known_info)+'\n'+'##output:'
            # print(ans1)
            response=multichat(ans1)
            print("当前为过滤后的答案",response)
            response=str(response)
            for exact_num in range(0,2):#未按照COT格式输出，重新生成
                if ('Analyzing' in response or 'Analyze' in response)and 'Known Information' in response and 'Answer' in response:
                   break
                print("生成格式不对")
                response=multichat(ans1)
                response=str(response)
                # print("未提取子问题的答案",response)
            # print("未提取原问题的答案",response)
            response=exact_answer(response)
            print("问题的答案",response)
            keyword=exact_answer3(response,question,','.join(known_info))
            print("关键词",keyword) 
            keyword_list.append(keyword)
            response_list.append(response)
            d[keyword] = d.setdefault(keyword, 0) + 1
            
            # setdefault()函数,如果键不存在于字典中，将会添加键并将值设为默认值
        most_common_word = Counter(keyword_list).most_common(1)[0][0]        
        if d[most_common_word]<2:
            for SCtime in range(0,4):
                ans1=ans_prompt+question+'\n'+'##konwn information:'+','.join(known_info)+'\n'+'##output:'
                # print(ans1)
                response=multichat(ans1)
                print("当前为过滤后的答案",response)
                response=str(response)
                for exact_num in range(0,2):#未按照COT格式输出，重新生成
                    if ('Analyzing' in response or 'Analyze' in response)and 'Known Information' in response and 'Answer' in response:
                        break
                    print("生成格式不对")
                    response=multichat(ans1)
                    response=str(response)
                    # print("未提取子问题的答案",response)
                # print("未提取原问题的答案",response)
                response=exact_answer(response)
                print("问题的答案",response)
                keyword=exact_answer3(response,question,','.join(known_info))
                print("关键词",keyword) 
                keyword_list.append(keyword)
                response_list.append(response)
                d[keyword] = d.setdefault(keyword, 0) + 1
        # ans1=ans_prompt+question+'\n'+'##konwn information:'+known_info+'\n'+'##output:'
        # response=multichat(ans1)
        # print("当前轮次为过滤的答案",response)
        # response=multichat_three(ans1,response,'So, answer me in the form of "The answer is:"')
        
        # print("问题的答案",response)
        print("正确的答案",answer)
        print("知道的信息",','.join(known_info))
        print("问题是",question)
        most_common_word = Counter(keyword_list).most_common(1)[0][0]

            # 找出这个单词在列表中的位置
        position = keyword_list.index(most_common_word)

        response=response_list[position]
        print("回复",response)


        temp_ans=can_answer2(question,response)
        print("是否能回答",temp_ans)#LLM 判断不准确，当做第二道保险
        if 'no' in temp_ans:
            response,most_common_word=cot_sc(question)
        print("最终总答案",response)
        print("最终总keyword",most_common_word)

        output.append({'question':question,'correct answer':answer,'model turn':num-1,'output keyword':most_common_word,'google_flag':search_flag,'response':response})
        # is_ans_prompt1=is_ans_prompt+'question:'+question+'\n'+'correct answer:'+answer+'\n'+'response:'+response+'\n'+'output:'
        # response=multichat(is_ans_prompt1)
        file_name = os.path.basename(__file__)
        #sendemail(message='正确率'+str(yes/(num2-num1)),subject=str(num1)+'-'+str(num2)+'正确率'+str(file_name))   
        file_name = os.path.basename(__file__)
            # Create a new log file with the current date as the filename
        fileName = datetime.datetime.now().strftime('day'+'%Y_%m_%d')+file_name
        with open('/data/zhangxiaoming/personal/RAG/'+fileName+'ans'+str(num1)+'-'+str(num2)+'.json', 'w', encoding='utf-8') as f:
            json.dump(output, f,indent=4)  
        if answer.lower() in most_common_word.lower():
            print("判断结果","yes")
            yes=yes+1
        else   :
            print("判断结果:no")
        print    
print("正确率",yes/(num2-num1)) 

file_name = os.path.basename(__file__)
sendemail(message='正确率'+str(yes/(num2-num1)),subject=str(num1)+'-'+str(num2)+'正确率'+str(file_name))   
file_name = os.path.basename(__file__)
    # Create a new log file with the current date as the filename
fileName = datetime.datetime.now().strftime('day'+'%Y_%m_%d')+file_name
with open('/data/zhangxiaoming/personal/RAG/'+fileName+'ans'+str(num1)+'-'+str(num2)+'.json', 'w', encoding='utf-8') as f:
    json.dump(output, f,indent=4) 
print("总使用google次数",google_time)   
log_file.close()      