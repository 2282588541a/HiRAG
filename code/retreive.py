import time
import requests
from elasticsearch import Elasticsearch
from transformers import AutoTokenizer, AutoModel,AutoModelForCausalLM
from src.contriever import Contriever
import datetime
import pickle
from elasticsearch import Elasticsearch
from transformers import AutoTokenizer, AutoModel,AutoModelForCausalLM
from openai import OpenAI
from Levenshtein import ratio
from src.contriever import Contriever
import re
import os
import wikipedia
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
from LLM import *
from prompt import *
ret_tokenizer = AutoTokenizer.from_pretrained('facebook/contriever-msmarco')
ret_model = Contriever.from_pretrained("facebook/contriever-msmarco").to('cuda')  
def embedding(message):
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
def dpr_search(message,keyword='',retry_num=1):#dpr 
    host = '127.0.0.1'
    print("dense retriever")
    port = 12345
    # if keyword=='':
    #     find1=find_prompt+ques+'\n'+"##output: "
    #     keyword=multichat(find1)
    if retry_num>1:
        return eles_search(message,retry_num=retry_num)#eles
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, port))
        except socket.error as msg:
            print(msg)
     

        s.sendall(message.encode())
        data = s.recv(1024*1024)

        res=str(data.decode())
        list_data = json.loads(res)

        s.close()
        if type(list_data)!=str:
            list_data = ' '.join(map(str, list_data))
        print("Results returned by the dense retriever",list_data)    
        return list_data
prompt_tokenizer = GPT2TokenizerFast.from_pretrained('gpt2')
prompt_tokenizer.pad_token = prompt_tokenizer.eos_token

def eles_search(ques,retry_num=0):#Retrieval using sparse reducers
    if retry_num>2:
        return 'No result#^'#This is a complete termination,
    print("elas")
    retriever = BM25(
        tokenizer=prompt_tokenizer,
        index_name='wikipedia_dpr',
        engine='elasticsearch',
        exclude_domains=['wikipedia.org', 'wikiwand.com', 'wiki2.org', 'wikimedia.org'])
    ans=retriever.retrieve([ques], topk=1)
    if len(ans)<2:
        print("Problem with sparse retriever")
        print(ans)
        return eles_search(ques,retry_num=retry_num+1)
    print("Results returned by the sparse searcher",ans[1][0][0])
    return json.dumps(ans[1][0][0])  
google_times=0 
google_cache={}    #Store cached links to avoid consuming a lot of search APIs
last_google_time=0         
def google_search2(googleques,ques,retry_num=0,end_time=0):#use searapi

    
    api_url="https://google.serper.dev/search"
    payload = json.dumps({
    "q": googleques
    })
    headers = {
    'X-API-KEY': 'xxxxxxxxxxx',#your api
    'Content-Type': 'application/json'
    }
    # api_url=str(api_url)
    print("The current problem is",googleques)
    # api_url='https://serpapi.com/search.json?q=Coffee&location=Austin,+Texas,+United+States&hl=en&gl=us&google_domain=google.com&api_key=b140edc501979ee129d8da2379ffa3ff915513e978567c7d7ab559d5fcc52454'
    # print("API URL:", api_url)
    if retry_num==0 or (googleques not in google_cache and retry_num>1):#First search or no cache
        try:
           
            response = requests.request("POST", url=api_url, headers=headers, data=payload)
            # global google_time
            # google_time=google_time+1
            print("Start searching Google using searapi",googleques)

            if response.status_code == 200:

                data = response.json()

                return_ans=''
                out_link=''
                if 'organic' not in data:
                    time.sleep(5)
                    print('google fault',data)
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
                        print('Using answerbox directly',filtered_data)
                    print("Google Question Answers",return_ans)
                    if 'link' in data['answerBox'] :
                            link=data['answerBox']['link']
                            if 'wikipedia.org' in link:
                                out_link=link
                                

                                                    
                    else:
                        if end_time==1:#Round 2 is not limited to Wikipedia
                            link=organic_results[0]['link']
                            return wiki_search(ques,link,retry_num)

                        for inst in organic_results:
                            link=inst['link']
                            if 'wikipedia.org' in link:
                                out_link=link

                                return_ans=return_ans+scrape_table(link)
                                break        
                else:
                    for inst in organic_results:
                        link=inst['link']
                        if 'wikipedia.org' in link:
                            out_link=link

                            return_ans=return_ans+scrape_table(link)
                            break        
                cache_instance={googleques:out_link}
                google_cache.update(cache_instance) #Update cache files             
                if return_ans=='':
                    print("outlink",out_link)
                    if out_link=='':
                        return google_search2(googleques=googleques,ques=ques,retry_num=retry_num+1,end_time=end_time)
                    print('return_ans is empty')
                    return wiki_search(ques=ques,link=out_link,retry_num=retry_num)
                
                return_ans=return_ans+' . '
                print('Google search returns the final result',return_ans)
                return return_ans
                # print(data['items'][0]['link'])
            else:
                print("Request failed, status code:", response.status_code)   
                return 'No result#^'
        except Exception as e:
            print("A network error occurred:", e)

            time.sleep(20)
            search_ques=ques
            if retry_num>1:

                return wiki_search2(search_ques,retry_num=retry_num)
            return google_search2(googleques,ques,retry_num=retry_num+1,end_time=end_time)        
    else:            
            if googleques not in google_cache:
                print("Not found in cache")
                print("googlecache",google_cache)
                return "empty list"
            str1=google_cache[googleques]
            if str1=='':
                print("The cache is empty, so the traditional solution is used.")
                if end_time==0:
                    return wiki_search2(ques,retry_num=retry_num-1)
                else:
                    return dpr_search(ques,'',retry_num=retry_num-1)
            if end_time==0:
                return wiki_search(ques,str1,retry_num=retry_num-1)
            else:
                return dpr_search(ques,str1,retry_num=retry_num-1)
            

#%%        
def split_sentence(sentence):
    words = sentence.split()  # Split the sentence into a list of words by spaces
    if len(words) <= 100:
        return [sentence]  # If the number of words does not exceed 100, return to the original sentence directly
    else:
        # If the number of words exceeds 100, split it into 100 words
        return [' '.join(words[i:i+100]) for i in range(0, len(words), 100)]
def wiki_search(ques,link,retry_num=0):#Issues and revisions This is a wiki search with keywords
    sear_ques=ques
    # global find_prompt
    content=''
    know_graph=''
    if retry_num>=2:

        find1=Prompt.find_prompt+ques+'\n'+"##output: "
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
            print("Start using Wikipedia to search for web pages, with the search terms",ques)
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
                print("Wikipedia search failed",e)
                return 'No result#^'
            print(topic)
            
            
            sentence.append(sear_ques)
            lasttime=time.time()
            if (len(topic)==0):
                if(temp_num==2):
                    return "empty list"
                print("Empty List")
                continue# 
                
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
                    print(" Similarity is too low")
                    content=''
                    continue
                content = wikipedia.page(topic[max_num],auto_suggest=False).content
                link=wikipedia.page(topic[max_num],auto_suggest=False).url
                know_graph=scrape_table(link)
                break_flag=True
                break
            except Exception  as e:
                print(e)
    else:            
        print("Start using Wikipedia assisted search at",link)
        know_graph=scrape_table(link)
        response = requests.get(link)
        soup = BeautifulSoup(response.text, 'html.parser')
        content = soup.get_text()
        
        # content = wikipedia.page(keyword,auto_suggest=False).content                    
    sentence=[]
    sentence.append(sear_ques)
    print("The sub-problem of retrieval is",ques)
            # page=page.content.split('.')
            # content=page.content
    if content=='':# 
        print(" The similarity of the subjects found is too low or there are many subsets")
        return "google#"+ques 
    parts= content.split('.')   
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
    embeddings1=embedding(sentence[0])
    # embeddings.append(embeddings1)
    sentence_sort = []
    for i in range(1,len(sentence)):
        
        
        # inputs = ret_tokenizer(sentence[i], padding=True, truncation=True, return_tensors="pt")
        # # inputs=inputs.to('cuda:0')
        # embeddings2 = ret_model(**inputs).squeeze()
        embeddings2=embedding(sentence[i])
        # embeddings.append(embeddings2)
        
        score=(embeddings1@embeddings2).item()
        sentence_sort.append({'score':score,'content':sentence[i]})
    sentence_sort.sort(key=lambda x:x['score'],reverse=True)
    # if retry_num>(len(sentence)-1)/2:# Too many retries
    if retry_num>4 or retry_num>=len(sentence_sort):# Too many retries
        print(" Too many retries")
        return "No result#"+ques
    # if retry_num==0:#
    ret_ans=''
    if retry_num<2:#
        ret_ans=ret_ans+know_graph
    if sentence_sort[retry_num]['content']==sentence[1]:#        
        print("Retrieved content",ret_ans+'\n'+sentence[1])        
        return ret_ans+'\n'+sentence[1]+'.'
    else:#The first paragraph is considered to be more important, so I added
        print("Retrieved content",ret_ans+'\n'+sentence[1]+'.\n'+sentence_sort[retry_num]['content']+'.')        
        return ret_ans+'\n'+sentence[1]+'\n'+sentence_sort[retry_num]['content']+'.'

def wiki_search2_online(ques,retry_num=0,end_time=0):#Issues and revision times This is a Wiki search without keywords
    sear_ques=ques#
    print("Start using Wikipedia assisted search, enter the question",ques)
    # global find_prompt
    if end_time>0 :
        return  dpr_search(ques,'',retry_num=retry_num)
    content=''

    find1=Prompt.find_prompt+ques+'\n'+"##output: "
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
        print("Start using Wikipedia to search for web pages, with the search terms",ques)
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
            print("Wikipedia search failed",e)
            return 'No result#^'
        
        
        
        sentence.append(sear_ques)
        lasttime=time.time()
        if (len(topic)==0):
            if(temp_num==2):
                return "empty list"
            print("Empty List")
            continue# 
            
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
        if max_similarity==2:#The special case of a complete subset
            temp=[]
            for tt in range(0,len(sim)):
                if sim[tt]==2:
                    temp.append((topic[tt],tt))#Find all the included situations
            max_num=temp[0][1] #The first identical character     
            if(len(temp)>1):
                print("There are multiple complete subsets")
                if retry_num==0:
                    content=''
                    break
            if (3<len(temp)-1 and retry_num==3):#3 is a super parameter, change the small pool here
                max_num=temp[retry_num-2][1]+1   #Replace the small pool,
        else:
            if retry_num==3:
                if max_num==0:#Change the pool only once
                    max_num=1
                else:
                    max_num=0    
        try:
            print(max_num)
            if max_similarity<0.3:
                print(" Similarity is too low")
                content=''
                continue

            know_graph=scrape_table_outline(topic[max_num])
            print("profile",know_graph)

            content = wikipedia.page(topic[max_num],auto_suggest=False).content
            break_flag=True
            break
        except Exception  as e:
            print(e)


                   
    sentence=[]
    sentence.append(sear_ques)
            # page=page.content.split('.')
            # content=page.content
    if content=='':# 
        print(" The similarity of the subjects found is too low or there are many subsets")
        return "google#"+ques 
    parts= content.split('.')   
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
    embeddings1=embedding(sentence[0])
    # embeddings.append(embeddings1)
    sentence_sort = []
    for i in range(1,len(sentence)):
        
        
        # inputs = ret_tokenizer(sentence[i], padding=True, truncation=True, return_tensors="pt")
        # # inputs=inputs.to('cuda:0')
        # embeddings2 = ret_model(**inputs).squeeze()
        embeddings2=embedding(sentence[i])
        # embeddings.append(embeddings2)
        
        score=(embeddings1@embeddings2).item()
        sentence_sort.append({'score':score,'content':sentence[i]})
    sentence_sort.sort(key=lambda x:x['score'],reverse=True)
    # if retry_num>(len(sentence)-1)/2:# Too many retries
    if retry_num>4  or retry_num>=len(sentence_sort):# Too many retries
        print(" Too many retries")
        return "No result#"+ques
    ret_ans=''
    if retry_num<2:
        ret_ans=ret_ans+know_graph
    if sentence_sort[retry_num]['content']==sentence[1]:#        
        print("Retrieved content",ret_ans+'\n'+sentence[1])        
        return ret_ans+'\n'+sentence[1]+'.'
    else:#The first paragraph is considered to be more important, so I added
        print("Retrieved content",ret_ans+'\n'+sentence[1]+'.\n'+sentence_sort[retry_num]['content']+'.')        
        return ret_ans+'\n'+sentence[1]+'\n'+sentence_sort[retry_num]['content']+'.'
def wiki_search2(ques,retry_num=0,end_time=0):#Issues and revision times This is a Wiki search without keywords
    sear_ques=ques
    # global find_prompt
    if end_time>0 :
        return  dpr_search(ques,'',retry_num=retry_num)
    content=''

    find1=Prompt.find_prompt+ques+'\n'+"##output: "
    sentence=[]
    content=''
    
    max_num=0
    ques=''
    know_graph=''
  
    sentence=[]
    ques=ques=multichat(find1)
    if ques.strip()=='':
        print(find1)
        ques=ques=multichat(find1)
        ques_parts = ques.split("is:", 1)
        if(len(ques_parts)>1):
            ques=ques_parts[1]
    print("Start using Wikipedia 2 assisted search, search terms are",ques)
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
        print("Wiki error, ans is",ans)


   
    
    
    sentence.append(sear_ques)
   
        
    max_similarity=-999
    sim=[]#All cases of subset
    for i in range(0,len(topic)):
        if ques.strip().lower() == topic[i].lower() or ques.strip().lower()+' (' in topic[i].lower():

            max_num=i
            max_similarity=2
            sim.append(2)
            continue
        similarity = ratio(sear_ques.lower(),re.sub(r'\(.*?\)', '', topic[i].lower()) )#Remove the content of the brackets and then calculate the similarity
        # print(similarity)
        sim.append(similarity)
        if similarity>max_similarity:
            max_similarity=similarity
            max_num=i
    if max_similarity==2:#The special case of a complete subset
        temp=[]
        for tt in range(0,len(sim)):
            if sim[tt]==2:
                temp.append((topic[tt],tt))#Find all the included situations
        max_num=temp[0][1] #The first identical character        
        if(len(temp)>1):
            print("There are multiple complete subsets")
            return "google#"+ques 
                
        if (3<len(temp)-1 and retry_num==3):#3 is a super parameter, change the small pool here
            max_num=temp[retry_num-2][1]+1   #Replace the small pool,
    else:
        if retry_num==3:
            if max_num==0:#Change the pool only once
                max_num=1
            else:
                max_num=0    

    
    
    
    print(max_num)
    if max_similarity<0.8:
        print("The correlation is too low")
        return "google#"+ques 
    title=topic[max_num]

    # know_graph=scrape_table(link)
    know_graph=scrape_table_outline(topic[max_num])
    print("profile",know_graph)
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
    if content=='':# 
        print(" The similarity of the subjects found is too low or there are many subsetswiki2")
        return "google#"+ques 
    parts= content.split('.')  
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
    embeddings1=embedding(sentence[0])
    # embeddings.append(embeddings1)
    sentence_sort = []
    for i in range(1,len(sentence)):
        
        
        # inputs = ret_tokenizer(sentence[i], padding=True, truncation=True, return_tensors="pt")
        # # inputs=inputs.to('cuda:0')
        # embeddings2 = ret_model(**inputs).squeeze()
        embeddings2=embedding(sentence[i])
        # embeddings.append(embeddings2)
        
        score=(embeddings1@embeddings2).item()
        sentence_sort.append({'score':score,'content':sentence[i]})
    sentence_sort.sort(key=lambda x:x['score'],reverse=True)
    # if retry_num>(len(sentence)-1)/2:# Too many retries
    if retry_num>4  or retry_num>=len(sentence_sort):# Too many retries
        print(" Too many retries")
        return "No result#"+ques
    ret_ans=''
    if retry_num<2:#
        ret_ans=ret_ans+know_graph
    if sentence_sort[retry_num]['content']==sentence[1]:#        
        print("Retrieved content",ret_ans+'\n'+sentence[1])        
        return ret_ans+'\n'+sentence[1]+'.'
    else:#The first paragraph is considered to be more important, so I added
        print("Retrieved content",ret_ans+'\n'+sentence[1]+'.\n'+sentence_sort[retry_num]['content']+'.')        
        return ret_ans+'\n'+sentence[1]+'\n'+sentence_sort[retry_num]['content']+'.'
def scrape_table(url, table_id='infobox vevent'):#Get answers to Wikipedia profiles in a timely manner

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

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

        return ''

    rows = table.find_all('tr')
    data = []
    for row in rows:
        cells = row.find_all(['td', 'th'])
        row_data = []
        for cell in cells:
            row_data.append(cell.get_text(strip=True))
        data.append(row_data)
   
    return ''.join(str(item) for item in data)[:6000]
def scrape_table_outline(title):
    #profile corpus
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
