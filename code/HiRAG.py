
#%%
from chatting import *
from LLM import *
from retreive import *
from prompt import Prompt
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
os.environ["http_proxy"] = "http://127.0.0.1:10101"
os.environ["https_proxy"] = "http://127.0.0.1:10101"
def loadfile(path):
    with open(path, 'r') as f:
        data = json.load(f)
    return data

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
            self.terminal = sys.stdout 
            self.path= os.path.join(path, filename)
            self.log_file = open(self.path, "a", encoding='utf8',) 
            print("Saving logs to:", os.path.join(self.path, filename)) 
 
        def write(self, message):
            '''
            Writes the message to both the terminal and the log file.

            :param message: The message to be written.
            '''
            self.terminal.write(message) 
            self.log_file.write(message)
            self.log_file.flush() 
 
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
def HiRAG(dataset):
    output=[]
    log_file = make_print_to_file(path='./')
    data = loadfile('dataset/'+dataset+'.json')
    print(1)
    num1=0
    num2=1
    print("num1",num1)
    print("num2",num2)
    for i in range(num1,num2):
            torch.cuda.empty_cache()  
            instance = data[i]
            question = instance['question']
            print("question:",question)
            answer = instance['answer']
            # evidenve = instance['question_decomposition']
            
            cot_prompt1=Prompt.cot_prompt+'\n'+'question:'+question+'\n'+'konwn information:'
            num=0
            search_flag=False
            # if i==20000:
            #         break
            known_info=[]
            lastquestion=[]
           
            times=0# 
            cot_messaeges=[]
            cot_messaeges.append({'role':'system','content':Prompt.cot_prompt})
            cot_messaeges.append({'role':'user','content':"Let's break down this complex question"+question})
            while num<6:
                torch.cuda.empty_cache()  
                print("Number of rounds + 1")
                num=num+1
                input=''
                
                print("Known information",','.join(known_info))  
                
                ques=confirm_ques(cot_messaeges)
                print("Subproblem generated",ques)
                if(ques.strip()==''):
                    ques=confirm_ques(cot_messaeges)
                    print("Reproduced sub-problem",ques)
                if " enough" in ques:
                    print("LLM believes that the information is sufficient",ques)
                    break
                if ques[0]=='0' and num>4:
                    print("The question is unreasonable")
                    break
                if ques.startswith("0"):
                    ques=ques[1:]
                if ques in lastquestion and times==0:#The question is repeated and not a case of backtracking
                    # known_info=known_info+buffer_instance['answer']+', '
                    print("Duplicate question")
                    break
                cot_messaeges.append({'role':'assistant','content':ques})
                find1=Prompt.find_prompt+ques+'\n'+"##output: "

                lastquestion.append(ques)
                retry_num=0
                response=''
                add_instance=''
                break_flag=False#The flag of whether to jump out, the two-layer loop jumps out from the inside
                times_flag=False #
                logit=1.0 #Initial default probability
                while True:
                    torch.cuda.empty_cache()  # 
                    if times>1:#
                        print("times>1")
                        response=direct_answer(Prompt.ques_prompt+ques+'\n##output:',ques)
                        temp_ans=can_answer(response,ques)
                        # response=multichat(exact_prompt4+ques+'\n##reply:'+response+'\n##output:')
                        print("LLM Answers",response)
                        # temp_ans=can_answer(response,ques)
                        print("Can answer",temp_ans)#LLM is not a good judgement, just a second line of defense
                        if 'yes' in temp_ans:
                                break #Continue to the next round of Q&A
                        else:
                            break_flag=True#No answer found, terminated
                            break  
                    if retry_num>10:
                        break_flag=True#No answer found, terminated
                        break 
                    search_ans=str(wiki_search2(ques,retry_num=retry_num,end_time=times))
                    # ques='what is the father of Alexandre Berthier, 3rd Prince of Wagram?'
                    # search_ans='twice#'
                    print("Searched knowledge",search_ans)
                    if retry_num>0:
                        print("Retry times",retry_num)
                    if search_ans=='empty list':#Unable to find relevant subject, re-obtain sub-question
                        # ques=confirm_ques(input,kind)
                        retry_num=retry_num+1
                        if ques[0]=='0' and num>=3:
                            break_flag=True
                            break
                        if ques in lastquestion and times==0:#
                            break_flag=True
                            break
                        lastquestion.pop()#
                        lastquestion.append(ques)
                        continue
                    if 'twice#' in search_ans:
                        search_ans= str(google_search2(ques,ques,retry_num,times))
                    if 'google#'in search_ans :
                        after_no_result = search_ans.split('google#', 1)[1]
                        print('There are too many confusing terms, start a Google search',after_no_result)
                        temp_num=-1#Save the answer containing the corresponding entity
                        for known_info_num in range(0,len(known_info)):
                            if after_no_result in known_info[known_info_num]:
                                temp_num=known_info_num
                                break
                        print("temp_num",temp_num)
                        google_ques=''
                        if 'question:' in ques:
                            google_ques=ques.split('question:', 1)[1]
                        else:    
                            google_ques=ques
                        if temp_num==-1:#
                            google_ques=google_ques #The current subject was not found in the previous answer
                        else:
                            enetity_prompt=Prompt.google_entity_prompt+'##entity:'+after_no_result+'\n'+'##information:'+known_info[temp_num]+'\n##output:'
                            eneity_temp=multichat(enetity_prompt)
                            print("The converted description is:",eneity_temp)
                            search_flag=True

                            google_ques=google_ques+' '+eneity_temp#The current subject is found in the previous answer   
                        
                        search_ans=google_search2(google_ques,ques,retry_num=retry_num,end_time=times)

                    if 'No result#'in search_ans :#
                        after_no_result = search_ans.split('No result#', 1)[1]
                        temp_num=-1
                        for known_info_num in range(0,len(known_info)):
                            if after_no_result in known_info[known_info_num]:
                                temp_num=known_info_num
                                break
                        print("temp_num",temp_num)  
                        if times==1:
                            break_flag=True
                            break  

                        num=num-1 #
                        lastquestion=lastquestion[:num]
                        known_info=known_info[:num]
                        if 'assistant' in cot_messaeges[-1]['role']:
                            cot_messaeges.pop()

                        times=times+1
                        times_flag=True
                        break
                    add_instance='##question:'+ques+'\n'+"##konwn information:"+search_ans+'\n'+'##output:'
                    ret=Prompt.ret_prompt+add_instance

                    response,key_temp=SCmultichat(ret,1,ques)
                    key_temp=key_temp.lower()  
                    print("Final Answer",response)
                    print("Final Keywords",key_temp)
                    key_temp=key_temp.lower()
                    temp_ans=can_answer(response,ques)
                    print("Can answer",temp_ans)#LLM is not a good judgement, just a second line of defense
                    if 'yes' in temp_ans:
                            break
                    else:
                        temp_logit= random.randint(1, 100)
                        threshold=(retry_num / 5) ** 2#Current Threshold
                        if temp_logit<threshold*100:#It is carried out with a certain probability. As retry_num increases, the probability increases, and the first-order derivative of the increase increases (both the first-order and second-order derivatives are greater than 0)
                            response=direct_answer(Prompt.ques_prompt+ques+'\n##output:',ques)
                            temp_ans=can_answer(response,ques)
                            # response=multichat(exact_prompt4+ques+'\n##reply:'+response+'\n##output:')
                            print("LLM Answers",response)
                            
                            print("Can answer",temp_ans)#LLM judgment is inaccurate，
                            if 'yes' in temp_ans:#If you can reply, proceed normally.
                                break
                    retry_num=retry_num+1
            
                    continue

                    break
                if break_flag==True: 
                    break   
                if times_flag==True:
                    continue    

                known_info.append(response)
                cot_messaeges.append({'role':'user','content':response})

                print("What is currently known",','.join(known_info)) 

            keyword_list=[]
            response_list=[]
            d = dict()
            print("Information to know",','.join(known_info))
            print("The problem is",question)
            for SCtime in range(0,3):
                ans1=Prompt.ans_prompt+question+'\n'+'##konwn information:'+','.join(known_info)+'\n'+'##output:'
                # print(ans1)
                response=multichat(ans1)
                print("Currently the answer is filtered",response)
                response=str(response)
                for exact_num in range(0,2):#Not output in COT format, regenerate
                    if ('Analyzing' in response or 'Analyze' in response)and 'Known Information' in response and 'Answer' in response:
                        break
                    print("The generated format is incorrect")
                    response=multichat(ans1)
                    response=str(response)

                response=exact_answer(response)
                print("Answers to questions",response)
                keyword=exact_answer3(response,question,','.join(known_info))
                print("Keywords",keyword) 
                keyword_list.append(keyword)
                response_list.append(response)
                d[keyword] = d.setdefault(keyword, 0) + 1
                
            most_common_word = Counter(keyword_list).most_common(1)[0][0]        
            if d[most_common_word]<2:
                for SCtime in range(0,4):
                    ans1=Prompt.ans_prompt+question+'\n'+'##konwn information:'+','.join(known_info)+'\n'+'##output:'
                    # print(ans1)
                    response=multichat(ans1)
                    print("Currently the answer is filtered",response)
                    response=str(response)
                    for exact_num in range(0,2):#Not output in COT format, regenerate
                        if ('Analyzing' in response or 'Analyze' in response)and 'Known Information' in response and 'Answer' in response:
                            break
                        print("The generated format is incorrect")
                        response=multichat(ans1)
                        response=str(response)

                    response=exact_answer(response)
                    print("Answers to questions",response)
                    keyword=exact_answer3(response,question,','.join(known_info))
                    print("Keywords",keyword) 
                    keyword_list.append(keyword)
                    response_list.append(response)
                    d[keyword] = d.setdefault(keyword, 0) + 1

            print("Correct Answer",answer)
            print("Information to know",','.join(known_info))
            print("The problem is",question)
            most_common_word = Counter(keyword_list).most_common(1)[0][0]

            position = keyword_list.index(most_common_word)

            response=response_list[position]
            print("response",response)


            temp_ans=can_answer2(question,response)
            print("Can answer",temp_ans)
            if 'no' in temp_ans:
                response,most_common_word=cot_sc(question)
            print("Final answer",response)
            print("Final total keyword",most_common_word)

            output.append({'question':question,'correct answer':answer,'model turn':num-1,'output keyword':most_common_word,'google_flag':search_flag,'response':response})
  
            with open('result/'+dataset+'ans'+str(num1)+'-'+str(num2)+'.json', 'w', encoding='utf-8') as f:
                json.dump(output, f,indent=4)  
            

    file_name = os.path.basename(__file__)

    file_name = os.path.basename(__file__)
    fileName = datetime.datetime.now().strftime('day'+'%Y_%m_%d')+file_name
    with open('result/'+dataset+'ans'+str(num1)+'-'+str(num2)+'.json', 'w', encoding='utf-8') as f:
        json.dump(output, f,indent=4)  
    log_file.close() 
def main():
    import argparse


    parser = argparse.ArgumentParser()


    parser.add_argument('--dataset', type=str, help='name for dataset')


    args = parser.parse_args()

  
    print(f'dataset: {args.dataset}')

    HiRAG(args.dataset)
main()