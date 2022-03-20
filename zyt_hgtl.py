# -*- coding:utf-8 -*-
# Author:Zhu Yuantong
#
#       *.                  *.
#      ***                 ***
#     *****               *****
#    .******             *******
#    ********            ********
#   ,,,,,,,,,***********,,,,,,,,,
#  ,,,,,,,,,,,*********,,,,,,,,,,,
#  .,,,,,,,,,,,*******,,,,,,,,,,,,
#      ,,,,,,,,,*****,,,,,,,,,.
#         ,,,,,,,****,,,,,,
#            .,,,***,,,,
#                ,*,.
# 这个文件是用来学习Git及Github的使用

from threading import Thread
import threading
import queue
from urllib import request
from urllib.request import urlopen
# import _ssl
import ssl

from bs4 import BeautifulSoup
import time
# import requests
# from lxml import etree

def get_word(url, id, sem, word_q):
    '''
    这个模块是为了爬取每章的题目和内容，并将结果写入text_dic字典
    :param url: 每章内容的网络地址；
    :param id: 该章内容在整个文件中的顺序号
    :return: 为了简单，没有用返回值
    '''
    # global text_dic
    text_dic1 = {}
    with sem:  # 在最大线程的限制下爬取
        text_lis = []  # 用于存储每章题目和内容的列表，并最终写入字典
        word_header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:55.0) Gecko/20100101 Firefox/55.0',
                       'Cookie': 'clickbids=43462; bgcolor=; font=; size=; fontcolor=; width=; Hm_lvt_1831f6c40ec480fc567fa5424b532d24=1634620892,1634621290; Hm_lpvt_1831f6c40ec480fc567fa5424b532d24=1634627605'}
        # 增加'Cookie'字段，是因为这个网站没有这个是爬不下来的

        try:
            req = request.Request(url, headers=word_header)
            # print(req)
        except Exception as e:
            print('!!!!!!!')

        while True:
            # 一个网页爬取出现错误的时候，一直爬，直到成功，
            # 这样虽然可以避免了偶发性的网页打不开的错误
            # 但是也有可能出现“死循环”的现象，以后再考虑，爬小说的时候应该不会
            try:
                html = request.urlopen(req, timeout=20)
                soup = BeautifulSoup(html, 'html.parser')
                if soup:
                    break
            except Exception as e:
                continue

        try:
            title = soup.find("div",{"class":"bookname"}).find("h1").get_text()
        except Exception as e:
            title = "第" + str(id) + "章"
        print(title)
        word = soup.find("div", {"id": "content"}).get_text()
        # if len(word) <100:
        #     while True:
        #         req = requests.get(url, headers=word_header)
        #         if req:
        #             break
        #     html = etree.HTML(req.text)
        #     word1 = html.xpath('//*[@id="content"]//text()')
        #     # word = word1[1:]
        #     word = ''.join(word1[1:])
            # content > ahref=""
        word = str(word).replace("    ", "\n")
        word = str(word).replace("\r", "\n")
        # 整个部分的id、属性等用于爬取的标志，都是具体分析得出的，要是换了网站，需要再分析
        text_lis.append(title+'\n'+word)
        # text_lis.append('\n'+word)
        # 这本书不用下题目，为了保持一致性，还是用了append，其实直接在后面写入word也可以
        # print(title+'\n'+word)
        key = str(id)
        # 这个序号来源于目录的顺序，因为是多线程爬取的，以后要依靠这个序号
        # 写入最终的文件，来确保书籍的顺序是正确的
        text_dic1[key] = text_lis
        word_q.put(text_dic1)
        # 把爬取的结果，组成一个字典，放入到队列中


def read_catal(url, add_head, url1, headers, cata_file):
    # 这个是用来获取目录的，不仅是爬取每章内容的具体地址，而且也是多线程爬取
    # 的结果的排序依据；
    # 因此，没有采用多线程的爬取；本身内容就应该不多，再考虑排序，就繁琐了
    catal = []
    i = 1  # 这个是用来表示页数的，用于翻页的

    # while True:
    html = urlopen(url)
    soup = BeautifulSoup(html, 'html.parser')

    s1 = soup.find_all("div", {"class": "box_con"})
    print(s1)
    for title in s1[1].find_all("a"):
        catal.append(add_head + title.attrs['href'])
    i += 1
    for cata in catal[12:]:  # 写到一个目录文件中，但不是必须的
        with open(cata_file, "a+") as f:
            try:
                f.write(cata + '\n')
            except:
                print("目录文件有错")

                # 返回的是一个每章内容的地址列表
    return catal[12:]


if __name__ == '__main__':
    url = 'https://www.xxxbiquge.com/43/43462/'
    url1 = 'https://www.xxxbiquge.com'
    cata_file = "护国天龙——目录.txt"
    text_file = "护国天龙.txt"
    add_head = "https://www.xxxbiquge.com"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:55.0) Gecko/20100101 Firefox/55.0'}
    ssl._create_default_https_context = ssl._create_unverified_context 
    # 创建默认不认证的https文本
    # 这个是抄来的，否则，urlopen的时候会出问题
    
    # global text_dic
    catal = read_catal(url, add_head, url1, headers, cata_file)
    print(catal)
    print("***************目录******************")
    # html = urlopen(url)  # 打开目录的网页，并进行分析
    # soup = BeautifulSoup(html, 'html.parser')

    '''
    #用于存储每章的内容，键值是依据目录得到的顺序号，因为是多线程爬取的，
    因此，写入字典的顺序会有变化，为了便于以后整理，所以用目录文件的顺序作为键值；
    同时，将每章的题目和内容形成列表，作为字段
    '''

    start = time.time()
    sem = threading.Semaphore(20)
    # 这个是为了限制线程的数量，有些网站用到2，而有些则可以到8以上，要试验而定
    i = 0  # 用于记录每章的顺序号
    threads = []  # 用于记录线程
    q = queue.Queue()  # 这个队列就是用来存放得到的文章内容，试图不用全局变量
    for item in catal[600:1000]:
        threads.append(Thread(target=get_word, args=(item, i, sem, q)))
        threads[-1].start()
        i += 1
    for t in threads:
        t.join()

    i = 0  # 依照顺序从字典中读出每章的题目和内容，然后再写入文件
    text_dic = {}
    print(q.qsize())
    i = 0
    m = q.qsize()
    while True:
        # 这个循环是为了从队列中取出所有的章节内容，形成了一个字典
        # 字典的“键”是章节的顺序
        # 这个地方的变量命名有点乱，懒得改了，反正功能没问题
        # 以后再说吧
        item = q.get()
        text_dic.update(item)
        i += 1
        if i == m:
            break

    i = 0
    while i < len(text_dic):
        with open(text_file, "a+", encoding="utf-8") as f:
            keys = str(i)
            tt = text_dic[keys]
            print(tt)
            f.write(tt[0] + '\n')
            # f.write(tt[1] + '\n')
            i += 1
    end = time.time()
    print("用时："+str(end-start))
