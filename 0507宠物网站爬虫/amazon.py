import requests,random,re,os,math,time
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver



CHROME_DRIVER_PATH = '/Users/huangmengfeng/PycharmProjects/2020_study_plan/0507宠物网站爬虫/chromedriver'



def getIPList():
    url = 'http://list.didsoft.com/get?email=yushiwei@shein.com&pass=4mmtwv&pid=http3000&showcountry=yes'
    resp = requests.get(url)
    msg = resp.text
    print(type(msg))
    ip_list_pattern = re.compile(r'[0-9]+.[0-9]+.[0-9]+.[0-9]+\:[0-9]{4}#[A-Z]{2}')
    ip_msg_list = ip_list_pattern.findall(msg)
    ip_obj_list = []
    for ip_msg in ip_msg_list:
        ip = ip_msg.split('#')[0]
        ip_obj_list.append(ip)
    print(ip_obj_list)
    return ip_obj_list



def get_dynamic_html(site_url):
    print('开始加载',site_url,'动态页面')
    proxy_args = '--proxy-server={0}'.format("http://" + ip_proxies_list[random.randint(0, len(ip_proxies_list) - 1)])
    chrome_options = webdriver.ChromeOptions()
    #ban sandbox
    #chrome_options.add_argument(proxy_args)
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    #use headless
    #chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--ignore-ssl-errors')
    driver = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH,chrome_options=chrome_options)
    #print('dynamic laod web is', site_url)
    driver.set_page_load_timeout(15)
    #driver.set_script_timeout(100)
    try:
        driver.get(site_url)
    except Exception as e:
        print(e, 'dynamic web load timeout')
        driver.execute_script('window.stop()')
        pass

    driver.set_window_size(1200, 960)
    data = driver.page_source
    soup = BeautifulSoup(data, 'html.parser')
    try:
        driver.quit()
    except:
        pass
    return soup



def createDir(base_dir,site_name):
    tmp_data_dir_1 = "{0}/{1}".format(base_dir,site_name)
    tmp_data_dir_2 = "{0}/{1}/{2}".format(base_dir,site_name,datetime.strftime(datetime.now(),'%Y%m%d'))
    out_dir = '{0}/OUT'.format(base_dir)
    path_arr = [base_dir,tmp_data_dir_1,tmp_data_dir_2,out_dir]
    for path in path_arr:
        if not os.path.exists(path):
            os.mkdir(path)
    record_path = '{0}/record.txt'.format(tmp_data_dir_2)
    if not os.path.exists(record_path):
        with open(record_path, 'a+', encoding="utf-8") as f:
            f.write('')
            f.close()
    return tmp_data_dir_2,out_dir,record_path



def analyzeSoup(soup,info_tmp):
    one_page_list = []
    article_list = soup.select('.s-result-item')
    for article_tag in article_list:
        data_asin = article_tag.attrs['data-asin']
        print(data_asin)
        if data_asin != '':
            one_page_list.append(article_tag)
    print(len(article_tag),len(one_page_list))




def getOneCatePageByPageNext(site_url,info_tmp):
    print('开始加载',site_url,'动态页面')
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--ignore-ssl-errors')
    driver = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH,chrome_options=chrome_options)
    driver.set_page_load_timeout(100)
    try:
        driver.get(site_url)
    except Exception as e:
        print(e, 'dynamic web load timeout')
        driver.execute_script('window.stop()')
        pass
    driver.set_window_size(1200, 960)
    data = driver.page_source
    soup = BeautifulSoup(data, 'html.parser')
    analyzeSoup(soup,info_tmp)
    for i in range(0,3):
        next_page_tag_list = driver.find_element_by_css_selector('.a-last')
        print(next_page_tag_list)
        next_page_tag_list.click()
        time.sleep(2)
        data = driver.page_source
        soup = BeautifulSoup(data, 'html.parser')
        analyzeSoup(soup, info_tmp)
    try:
        driver.quit()
    except:
        pass



if __name__ == '__main__':
    url_excel_path_0 = '/Users/huangmengfeng/Desktop/宠物竞品爬虫.xlsx'
    base_dir_0 = '/Users/huangmengfeng/Desktop/PET_SCRIPY'
    site_name_0 = 'www.amazon.com'

    tmp_data_dir_0, out_dir_0, record_path_0 = createDir(base_dir_0, site_name_0)

    url_0 = 'https://www.amazon.com/s?k=Dog+Sweaters+%26+Hoodies&ref=nb_sb_noss'
    info_tmp_0 = {
        'brand': site_name_0,
        'cate_name': 'Dog Sweaters & Hoodies',
        'cate_remark':'毛衣卫衣',
        'desc': '',
        'price': 0,
        'old_price': 0,
        'url': ''
    }
    getOneCatePageByPageNext(url_0,info_tmp_0)