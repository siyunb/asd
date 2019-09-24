# -*- coding: utf-8 -*-
"""
Created on Wed Aug 28 14:41:14 2019

@author: Bokkin Wang
"""

import sys
import bs4
import  random
import re
import os
sys.path.append("D:/bigdatahw/pan_paper/code/crawl")
from selenium import webdriver 
from multiprocessing.dummy import Pool               #selenium实现自动化
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
from parser_for_JASA import *
import time
os.chdir("D:/bigdatahw/pan_paper/top4")

# section 1
def litte_parser(driver):
    html=driver.page_source
    soup=bs4.BeautifulSoup(html,'html.parser',from_encoding="gb18030")
    return soup

def load_name(path):
    csvnames = os.listdir(path)
    csvnames = [os.path.splitext(csvname)[0] for csvname in csvnames]
    return csvnames

first_url = 'https://www.tandfonline.com'
driver =webdriver.Chrome('C:/Program Files (x86)/Google/chrome/Application/chromedriver.exe')   #打开浏览器
driver.get('https://www.tandfonline.com/loi/uasa20')
year_all = litte_parser(driver).findAll('li', {"class": "vol_li "})

complete_url = [] 
i = 114
j = 2019
for year_volume in year_all[0:25]:
    year_url = first_url + year_volume.find('a').get('href')
    driver.get(year_url)
    id_num = "vol_%d_%d" %(i,j) 
    volume_all = litte_parser(driver).find('li', {"id": id_num}).findAll('li')
    for one_volume in volume_all:
        volume_url = first_url + one_volume.find('a').get('href')
        complete_url.append(volume_url)
    i = i-1
    j = j-1
    
driver.quit()       

#section 2
def list_of_groups(init_list, children_list_len):
    list_of_groups = zip(*(iter(init_list),) *children_list_len)
    end_list = [list(i) for i in list_of_groups]
    count = len(init_list) % children_list_len
    end_list.append(init_list[-count:]) if count !=0 else end_list
    return end_list

#section 3
def pool_url(url_list):
    driver =webdriver.Chrome('C:/Program Files (x86)/Google/chrome/Application/chromedriver.exe')   #打开浏览器
    data_path = 'D:/bigdatahw/pan_paper/top4'
    first_url = 'https://www.tandfonline.com'
    result = {'title':[],'publish_date':[],'reference':[]}
    columns = ['title','publish_date','reference']        
    for volume_url in url_list:        
        driver.get(volume_url) 
        issue = litte_parser(driver)
        reference_part = issue.findAll('a', {"class":"ref nowrap references"})
        reference_url = [first_url+item.get('href') for item in reference_part]
        for article_url in reference_url:
            driver.get(article_url)
            time.sleep(5)
            try:         
                article_content = litte_parser(driver)
                result = parse(article_content,result)
            except:
                pass
    if 'JASA' not in load_name('D:/bigdatahw/pan_paper/top4'):
        pd.DataFrame(result).to_csv(data_path + "/JASA.csv",index=False,columns=columns)    
        print('JASA' +'    succeed!')
    else:
        pd.DataFrame(result).to_csv(data_path + "/JASA.csv",index=False,columns=columns,header=False,mode = 'a')    
        print('JASA' +'   add'+'    succeed!')
    driver.quit()       

#section 4
def pool_url_bu(url_list):
    driver =webdriver.Chrome('C:/Program Files (x86)/Google/chrome/Application/chromedriver.exe')   #打开浏览器
    data_path = 'D:/bigdatahw/pan_paper/top4'
    first_url = 'https://www.tandfonline.com'
    all_title =list( pd.read_csv(data_path + "/JASA.csv",encoding="ISO-8859-1")['title'])
    result = {'title':[],'publish_date':[],'reference':[]}
    columns = ['title','publish_date','reference']        
    for volume_url in url_list:        
        driver.get(volume_url) 
        issue = litte_parser(driver)
        reference_part = issue.findAll('a', {"class":"ref nowrap references"})
        reference_url = [first_url+item.get('href') for item in reference_part]
        try:
            judge_url = reference_url[1]
            driver.get(judge_url)
            time.sleep(5)
            article_content = litte_parser(driver)
            judge_title = article_content.find('span',{'class':'NLM_article-title hlFld-title'}).text.strip()
            if judge_title in all_title:
                driver.quit()
            else:
                for article_url in reference_url:
                    driver.get(article_url)
                    time.sleep(5)
                    try:
                        article_content = litte_parser(driver)
                        result = parse(article_content,result)
                    except:
                        pass
                if 'JASA' not in load_name('D:/bigdatahw/pan_paper/top4'):
                    pd.DataFrame(result).to_csv(data_path + "/JASA.csv",index=False,columns=columns)    
                    print('JASA' +'    succeed!')
                else:
                    pd.DataFrame(result).to_csv(data_path + "/JASA.csv",index=False,columns=columns,header=False,mode = 'a')    
                    print('JASA' +'   add'+'    succeed!')
                driver.quit()
        except:
            driver.quit()
    url_list.pop()
    
  
if  __name__=='__main__':
    url_pool = list_of_groups(complete_url,1)
    p=Pool(1)
    p.map(pool_url_bu, url_pool1)
    p.close()
    p.join()  

url_pool1 = []
for i in url_pool:
    if not i in url_pool1:
        url_pool1.append(i)
print(url_pool1)

url_pool1.pop(0)

