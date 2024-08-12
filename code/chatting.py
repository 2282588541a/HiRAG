from prompt import Prompt
from LLM import *
from retreive import *
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
from BM25 import BM25
from BM25_wiki import BM25_1
import transformers
from transformers import GPT2TokenizerFast
import socket
import json
import torch
import threading
def confirm_ques(message):
    ques=decomposechat(message)
    ques_list=[]


    ques_list.append(ques)
    print("Decomposed sub-problems",ques)
    for iii in range(0, 5):
        ques=decomposechat(message)
        
        ques_list.append(ques)
    similarities = [ratio(ques_list[i].lower(), ques_list[j].lower()) for i in range(len(ques_list)) for j in range(i+1, len(ques_list))]
    avg_similarity = sum(similarities) / len(similarities)

    print("Average similarity",avg_similarity)
    if avg_similarity>0.9:
        return ques_list[0]
    else:
        return '0'+ques_list[0]#Returning 0 means the problem is not reasonable and will be processed again later
def exact_answer(mess):
    # try:
    parts = mess.split("Answer the Question", 1)

#Take the part after "answer"
    if len(parts) > 1:
        result = parts[1]
        
    else:
        result =multichat(Prompt.exact_prompt+mess) 
    return result   
def exact_answer2(mess,question):#Sub-question extraction keyword
    return multichat(Prompt.exact_prompt2+mess+"\n##question:"+question+'\n'+"##output:") 
def exact_answer3(mess,question,info):#Extract keywords from parent questions
    return multichat(Prompt.exact_prompt3+mess+'.'+info+"\n##question:"+question+'\n'+"##output:") 
def exact_answer4(mess,question):#Extract keywords from parent questions
    return multichat(Prompt.exact_prompt3+mess+"\n##question:"+question+'\n'+"##output:") 
def can_answer(mess,question):#Determine whether the question can be answered
    # return multichat(can_answer_prompt+mess+"\n##question:"+question+'\n'+"##output:")
    ans_num=0
    for SC in range (0,5):#self-constitency
        ans_flag=multichat(Prompt.can_answer_prompt+mess+"\n##question:"+question+'\n'+"##output:")
        if 'yes' in ans_flag:
            ans_num=ans_num+1
    if ans_num>2:
        return 'yes'
    else:
        return 'no'
def can_answer1(known_info,question):#Determine whether the question can be answered
    ans_num=0
    for SC in range (0,5):#self-constitency
        ans_flag=multichat(Prompt.can_answer_prompt1+question+"\n##konwn information:"+known_info+'\n'+"##output:")
        if 'yes' in ans_flag:
            ans_num=ans_num+1
    if ans_num>2:
        return 'yes'
    else:
        return 'no'
def can_answer2(question,response):#Determine whether the answer is acceptable
    # return multichat(can_answer_prompt+mess+"\n##question:"+question+'\n'+"##output:")
    ans_num=0
    for SC in range (0,5):#self-constitency
        ans_flag=multichat(Prompt.can_answer_prompt2+question+"\n##response:"+response+'\n'+"##output:")
        if ' no ' in ans_flag or 'not ' in ans_flag:
            ans_num=ans_num+1
    if ans_num>2:
        return 'no'
    else:
        return 'yes'
def direct_answer(message,question):#Direct answer to sub-question
    keyword_list=[]
    response_list=[]
    d = dict()
    for SCtime in range(0,3):
        
        response=multichat(message)

        keyword=multichat(Prompt.exact_prompt2+response+"\n##question:"+question+'\n'+"##output:") 
        print("Sub-question keywords",keyword) 
        keyword_list.append(keyword)
        response_list.append(response)
        d[keyword] = d.setdefault(keyword, 0) + 1
        
      # setdefault() function, if the key does not exist in the dictionary, it will add the key and set the value to the default value
    most_common_word = Counter(keyword_list).most_common(1)[0][0]        
    if d[most_common_word]<2:
        for SCtime in range(0,3):
        

            response=str(response)
            
            keyword=multichat(Prompt.exact_prompt2+response+"\n##question:"+question+'\n'+"##output:") 
            print("Sub-question keywords",keyword) 
            keyword_list.append(keyword)
            response_list.append(response)
            d[keyword] = d.setdefault(keyword, 0) + 1

    most_common_word = Counter(keyword_list).most_common(1)[0][0]


    position = keyword_list.index(most_common_word)

    response=response_list[position]
    print("Final sub-question answer",response)
    print("Final sub-question keywords",most_common_word)
    return response   
def SCmultichat(message,times,question):#Subproblem SC alignment
    keyword_list=[]
    response_list=[]
    d = dict()
    for SCtime in range(0,3):
        
        response=multichat(message)
        response=str(response)
        for exact_num in range(0,2):#Not output in COT format, regenerate
            if ('Analyzing' in response or 'Analyze' in response)and 'Known Information' in response and 'Answer' in response:
                break
            print("The generated format is incorrect")
            response=multichat(message)
            response=str(response)

        response=exact_answer(response)
        keyword=multichat(Prompt.exact_prompt2+response+"\n##question:"+question+'\n'+"##output:") 
        print("Sub-question keywords",keyword) 
        keyword_list.append(keyword)
        response_list.append(response)
        d[keyword] = d.setdefault(keyword, 0) + 1
        
    most_common_word = Counter(keyword_list).most_common(1)[0][0]        
    if d[most_common_word]<2:
        for SCtime in range(0,3):
        
            response=multichat(message)
            response=str(response)
            for exact_num in range(0,2):##Not output in COT format, regenerate
                if ('Analyzing' in response or 'Analyze' in response)and 'Known Information' in response and 'Answer' in response:
                    break
                print("The generated format is incorrect")
                response=multichat(message)
                response=str(response)

            response=exact_answer(response)
            print("Answers to sub-questions",response)
            keyword=multichat(Prompt.exact_prompt2+response+"\n##question:"+question+'\n'+"##output:") 
            print("Sub-question keywords",keyword) 
            keyword_list.append(keyword)
            response_list.append(response)
            d[keyword] = d.setdefault(keyword, 0) + 1

    most_common_word = Counter(keyword_list).most_common(1)[0][0]

    position = keyword_list.index(most_common_word)

    response=response_list[position]
    print("Final sub-question answer",response)
    print("Final sub-question keywords",most_common_word)
    return response,most_common_word
def cot_sc(question):
    try:
        keyword_list=[]
        response_list=[]
        d = dict()
        for SCtime in range(0,3):
            ans1=question+"Let's think this question step by step!"
            # print(ans1)
            response=multichat(question+"Let's think this question step by step!")
            print("Currently the answer is filtered",response)
            response=str(response)
           
            print("Answers to questions",response)
            keyword=exact_answer4(response,question)
            print("Keywords",keyword) 
            keyword_list.append(keyword)
            response_list.append(response)
            d[keyword] = d.setdefault(keyword, 0) + 1
            
        most_common_word = Counter(keyword_list).most_common(1)[0][0]        
        if d[most_common_word]<2:
            for SCtime in range(0,4):
                ans1=question+"Let's think this question step by step!"
                # print(ans1)
                response=multichat(ans1)
                print("Currently the answer is filtered",response)
                response=str(response)

                print("Answers to questions",response)
                keyword=exact_answer4(response,question)
                print("Keywords",keyword) 
                keyword_list.append(keyword)
                response_list.append(response)
                d[keyword] = d.setdefault(keyword, 0) + 1

        most_common_word = Counter(keyword_list).most_common(1)[0][0]

        position = keyword_list.index(most_common_word)

        response=response_list[position]
        print("Final Answer",response)
        

        print("Final keyword",most_common_word)
        return response,most_common_word
    except Exception as e:
        ans1=question+"Let's think this question step by step!"
            # print(ans1)
        response=multichat(question+"Let's think this question step by step!")
        most_common_word=exact_answer4(response,question)
        return response,most_common_word
