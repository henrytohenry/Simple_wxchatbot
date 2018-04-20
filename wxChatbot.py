#%%
# Step 1:检测用户所输入的问题
# Step 2:将检测到的问题与问题库进行比对
# Step 3:给出与用户问题比对的结果，输出问题排行或者转人工
# Step 4:用户可以自由选择所需要回答的问题
#
# ==============================================================================

# -*- coding: utf-8 -*-
import itchat
import jieba
import re
from jieba import analyse
import jieba.posseg as psg

jieba.load_userdict('dict.txt')

#读取文件
def read_from_file(file_name):
    with open(file_name,"r",encoding='utf-8') as fp:
        words = fp.read()
    return words

#获取停词
def stop_words(stop_word_file):
    words = read_from_file(stop_word_file)
    result = jieba.cut(words)
    new_words = []
    for r in result:
        new_words.append(r)
    #print(new_words)
    return set(new_words)

#删除停词
def del_stop_words_otherwords(words,stop_words_set):
    result = psg.cut(words)
    new_words = []
    for word, flag in result:
        if (flag == 'v' or flag == 'n' or flag == 'x') and word not in stop_words_set:
            new_words.append(word)
    return new_words

#模糊匹配
def fuzzyfinder2(user_input,datacollection):
    suggestions=[]
    #pattern='.*'.join(user_input)
    pattern=user_input
    regex = re.compile(pattern)
    for item in datacollection:
        match = regex.search(item)
        if match:
            suggestions.append((item,len(match.group())))
    return suggestions

questioncollection=[]

stop_words = stop_words('stopword.txt')

#检测问题库
def collect_question(question_package):
    collection=[]
    with open(question_package, 'r',encoding='utf-8') as f3:
        for i in f3.readlines():
            i=i.encode('utf-8').decode('utf-8-sig')
            i = i.strip('\n')
            collection.append(str(i))
    return collection

#自动识别问题
def auto_detected_Question(Question,stop_words):
    #Output=[]
    new_words = del_stop_words_otherwords(Question, stop_words)
    rs = {}
    # 这部分是最重要的，对匹配到的长度进行加权
    questioncollection = collect_question('问题库.txt')
    for item in new_words:
        if (fuzzyfinder2(item, questioncollection)) != []:
            ff = fuzzyfinder2(item, questioncollection)
            for _ in range(len(ff)):
                if ff[_][0] in rs.keys():
                    rs[ff[_][0]] += ff[_][1]
                if ff[_][0] not in rs.keys():
                    rs[ff[_][0]] = ff[_][1]
    sorted_x = sorted(rs.items(), key=lambda d: d[1], reverse=True)
    l = len(sorted_x)
    qo = []
    qo_rank=[]
    for i in range(l):
        # print(i+1,'.',sorted_x[i])
        qo.append(sorted_x[i][0])
        qo_rank.append(str(i+1)+'.'+sorted_x[i][0])
        #print(i + 1, '.', qo[i + 1])
        #itchat.send(qo,msg['FromUserName'])
    qo.append('转人工')
    qo_rank.append(str(l+1)+'.转人工')
    return qo,qo_rank

qo=[]
#qo_rank=[]

@itchat.msg_register(itchat.content.TEXT)


#文本回复
def text_reply(msg):
    #qo, qo_rank = auto_detected_Question(msg['Text'], stop_words)
    #print(qo,qo_rank)
    #print(sorted_x)
    global qo,qo_rank,result
    if msg['Text'].isdigit():
        if qo:
            if int(msg['Text'])>len(qo):
                itchat.send('你输入的数字超过范围',toUserName=msg['FromUserName'])
            else:
                word=read_from_file('知识库/'+qo[int(msg['Text'])-1]+'.txt')
                itchat.send(word,toUserName=msg['FromUserName'])
        else:
            itchat.send('请发送你想咨询的问题',toUserName=msg['FromUserName'])
    if not msg['Text'].isdigit():
        #with open('ww.txt','a') as f:
            #f.write(msg['Text']+'\n')
        qo, qo_rank = auto_detected_Question(msg['Text'], stop_words)
        result='您想咨询的问题是：'+msg['Text']+'\n\n'+'系统为你匹配如下问题：\n\n'
        #qo,sorted_x = auto_detected_Question(msg['Text'], stop_words)
        for i in range(len(qo_rank)):
            result=result+qo_rank[i]+'\n\n'
        result=result+'请直接回复您要选择的数字'
        itchat.send(result, toUserName=msg['FromUserName'])


    #print(msg.text)
    #return msg.text

itchat.auto_login(hotReload=True)
itchat.run()

