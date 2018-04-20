#%%
# Step 1:����û������������
# Step 2:����⵽���������������бȶ�
# Step 3:�������û�����ȶԵĽ��������������л���ת�˹�
# Step 4:�û���������ѡ������Ҫ�ش������
#
# ==============================================================================

# -*- coding: utf-8 -*-
import itchat
import jieba
import re
from jieba import analyse
import jieba.posseg as psg

jieba.load_userdict('dict.txt')

#��ȡ�ļ�
def read_from_file(file_name):
    with open(file_name,"r",encoding='utf-8') as fp:
        words = fp.read()
    return words

#��ȡͣ��
def stop_words(stop_word_file):
    words = read_from_file(stop_word_file)
    result = jieba.cut(words)
    new_words = []
    for r in result:
        new_words.append(r)
    #print(new_words)
    return set(new_words)

#ɾ��ͣ��
def del_stop_words_otherwords(words,stop_words_set):
    result = psg.cut(words)
    new_words = []
    for word, flag in result:
        if (flag == 'v' or flag == 'n' or flag == 'x') and word not in stop_words_set:
            new_words.append(word)
    return new_words

#ģ��ƥ��
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

#��������
def collect_question(question_package):
    collection=[]
    with open(question_package, 'r',encoding='utf-8') as f3:
        for i in f3.readlines():
            i=i.encode('utf-8').decode('utf-8-sig')
            i = i.strip('\n')
            collection.append(str(i))
    return collection

#�Զ�ʶ������
def auto_detected_Question(Question,stop_words):
    #Output=[]
    new_words = del_stop_words_otherwords(Question, stop_words)
    rs = {}
    # �ⲿ��������Ҫ�ģ���ƥ�䵽�ĳ��Ƚ��м�Ȩ
    questioncollection = collect_question('�����.txt')
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
    qo.append('ת�˹�')
    qo_rank.append(str(l+1)+'.ת�˹�')
    return qo,qo_rank

qo=[]
#qo_rank=[]

@itchat.msg_register(itchat.content.TEXT)


#�ı��ظ�
def text_reply(msg):
    #qo, qo_rank = auto_detected_Question(msg['Text'], stop_words)
    #print(qo,qo_rank)
    #print(sorted_x)
    global qo,qo_rank,result
    if msg['Text'].isdigit():
        if qo:
            if int(msg['Text'])>len(qo):
                itchat.send('����������ֳ�����Χ',toUserName=msg['FromUserName'])
            else:
                word=read_from_file('֪ʶ��/'+qo[int(msg['Text'])-1]+'.txt')
                itchat.send(word,toUserName=msg['FromUserName'])
        else:
            itchat.send('�뷢��������ѯ������',toUserName=msg['FromUserName'])
    if not msg['Text'].isdigit():
        #with open('ww.txt','a') as f:
            #f.write(msg['Text']+'\n')
        qo, qo_rank = auto_detected_Question(msg['Text'], stop_words)
        result='������ѯ�������ǣ�'+msg['Text']+'\n\n'+'ϵͳΪ��ƥ���������⣺\n\n'
        #qo,sorted_x = auto_detected_Question(msg['Text'], stop_words)
        for i in range(len(qo_rank)):
            result=result+qo_rank[i]+'\n\n'
        result=result+'��ֱ�ӻظ���Ҫѡ�������'
        itchat.send(result, toUserName=msg['FromUserName'])


    #print(msg.text)
    #return msg.text

itchat.auto_login(hotReload=True)
itchat.run()

