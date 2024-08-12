class Prompt:
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