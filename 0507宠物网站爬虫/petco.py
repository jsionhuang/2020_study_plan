import requests,os,re,math,xlwt,random,time
import pandas as pd
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from selenium import webdriver
from datetime import datetime



CHROME_DRIVER_PATH = '/home/babel/work_space/hot_babel_2/20200505_pet_scrapy/chromedriver'



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



def get_static_html(site_url):
    print('loading static html',site_url)
    headers_list = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.79 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0 ',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
    ]
    headers = {
        'user-agent': headers_list[random.randint(0,len(headers_list))-1],
        'Connection': 'keep - alive'
    }
    proxies = {
        'http': "http://" + ip_proxies_list[random.randint(0, len(ip_proxies_list) - 1)]
    }
    try:
        #resp = requests.get(site_url, headers=headers)
        resp = requests.get(site_url, headers=headers,proxies=proxies)
    except Exception as inst:
        print(inst)
        requests.packages.urllib3.disable_warnings()
        resp = requests.get(site_url, headers=headers,verify=False)
    soup = BeautifulSoup(resp.text, 'html.parser')
    return soup



def get_dynamic_html(site_url):
    print('开始加载',site_url,'动态页面')
    #proxy_args = '--proxy-server={0}'.format("http://" + ip_proxies_list[random.randint(0, len(ip_proxies_list) - 1)])
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
    time.sleep(2)
    data = driver.page_source
    soup = BeautifulSoup(data, 'html.parser')
    try:
        driver.quit()
    except:
        pass
    return soup



def getOneCatePageByPageNext(site_url,info_tmp):
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
    driver.set_page_load_timeout(100)
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
    analyzeSoup(soup,info_tmp)
    for i in range(0,3):
        next_page_tag_list = driver.find_element_by_css_selector('.right_arrow')
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



def analyzeSoup(soup,info_tmp):
    one_page_list = []
    article_list = soup.select('.prod-tile')
    for article in article_list:
        info = info_tmp.copy()
        desc_tag_list = article.select('.product-name')
        price_tag_list = article.select('.product-price')
        if len(price_tag_list) == 0 or len(desc_tag_list) == 0:
            pass
        else:
            desc_tag = desc_tag_list[0]
            price_tag = price_tag_list[0]
            link_tag  = desc_tag.select('a')[0]

            info['desc'] = desc_tag.text.replace('\n', '').replace('\t', '').strip()

            price_pattern = re.compile(r'[0-9]+.[0-9]{2}')
            price_arr = price_pattern.findall(price_tag.text)



            info['url'] = link_tag.attrs['href']


            if len(price_arr) > 0:
                info['price'] = price_arr[0]
                if len(price_arr) == 1:
                    info['old_price'] = price_arr[0  ]
                elif len(price_arr) == 2:
                    info['old_price'] = price_arr[1]
                print(info)
                one_page_list.append(info)

    return one_page_list




def getTotalPageNum(url,info_tmp):
    soup = get_static_html(url)
    total_tag_list = soup.select('.results-total')
    if len(total_tag_list) > 0:
        total_tag = total_tag_list[0]
        print(total_tag.text)
        total_pattern = re.compile(r'[0-9]+')
        total_num_str = total_pattern.findall(total_tag.text)[0]
        total_num = int(total_num_str)
        page_num = math.ceil(total_num / 48)

        one_page_list = analyzeSoup(soup,info_tmp)

        return page_num,one_page_list
    else:
        return 0,[]


def getPageList(url,info_tmp):
    soup = get_dynamic_html(url)
    return analyzeSoup(soup,info_tmp)



def exportToExcel(heads,task_done,path,filename):
    if not os.path.exists(path):
        os.makedirs(path)
    task_xls = xlwt.Workbook(encoding='utf-8')
    task_sheet1 = task_xls.add_sheet('sheet1')
    #表头
    header_allign = xlwt.Alignment()
    header_allign.horz = xlwt.Alignment.HORZ_CENTER
    header_style = xlwt.XFStyle()
    header_style.alignment = header_allign
    for i in  range(len(heads)):
        task_sheet1.col(i).width = 12000
        task_sheet1.write(0,i,heads[i],header_style)
    #开始插入
    for i in range(len(task_done)):
        for j in range(len(heads)):
            task_sheet1.write(i+1,j,task_done[i][heads[j]])
    print(os.path.join(path,filename))
    task_xls.save(os.path.join(path,filename))
    return filename



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
        os.mknod(record_path)
    return tmp_data_dir_2,out_dir,record_path



def getDoneUrl(path):
    done_url = []
    with open(path, 'r', encoding="utf-8") as f:
        url_list = f.readlines()
        for url in url_list:
            done_url.append(url.rstrip('\n'))
        print(done_url)
    return done_url



def addDoneUrl(path,content):
    try:
        with open(path, 'a+', encoding="utf-8") as f:
            f.write(content + '\n')
            f.close()
    except Exception as e:
        print(e)


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
        next_page_tag_list = driver.find_element_by_css_selector('.right_arrow')
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


def getOneCatePage(url,info_tmp,info_flied_arr,tmp_data_dir,record_path):
    done_url = getDoneUrl(record_path)
    if url not in done_url:
        total_page_num,first_page_list = getTotalPageNum(url,info_tmp)
        if total_page_num == 0:
            pass
        elif total_page_num == 1 :
            exportToExcel(info_flied_arr,first_page_list,tmp_data_dir,
                          '{0}_{1}.xlsx'.format(info_tmp['cate_name'],1))
            addDoneUrl(record_path,url)
        else:
            '''
            for i in range(1,total_page_num+1):
                
                page_url = '{0}#facet:&productBeginIndex:{1}&orderBy:&pageView:grid&minPrice:&maxPrice:&pageSize:48&'.format(url,(i-1)*48)
                if page_url not in done_url:
                    now_page_list = getPageList(page_url,info_tmp)
                    exportToExcel(info_flied_arr, now_page_list, tmp_data_dir,
                                  '{0}_{1}.xlsx'.format(info_tmp['cate_name'], i))
                    #addDoneUrl(record_path, page_url)
            '''
            print('开始加载', url, '动态页面')
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--ignore-ssl-errors')
            driver = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH, chrome_options=chrome_options)
            driver.set_page_load_timeout(100)
            try:
                driver.get(url)
            except Exception as e:
                print(e, 'dynamic web load timeout')
                driver.execute_script('window.stop()')
                pass
            driver.set_window_size(1200, 960)
            data = driver.page_source
            soup = BeautifulSoup(data, 'html.parser')
            now_page_list_1 = analyzeSoup(soup, info_tmp)
            exportToExcel(info_flied_arr, now_page_list_1, tmp_data_dir,
                          '{0}_{1}.xlsx'.format(info_tmp['cate_name'], 1))
            for i in range(2,total_page_num+1):
                next_page_tag_list = driver.find_element_by_css_selector('.right_arrow')
                print(next_page_tag_list)
                next_page_tag_list.click()
                time.sleep(2)
                data = driver.page_source
                soup = BeautifulSoup(data, 'html.parser')
                analyzeSoup(soup, info_tmp)
                now_page_list_i = analyzeSoup(soup, info_tmp)
                exportToExcel(info_flied_arr, now_page_list_i, tmp_data_dir,
                              '{0}_{1}.xlsx'.format(info_tmp['cate_name'], i))
            try:
                driver.quit()
            except:
                pass
            addDoneUrl(record_path, url)


def getAllCatePage(cate_list,site_name,tmp_data_dir,record_path):
    for cate in cate_list:
        info_tmp = {
            'brand': site_name,
            'cate_name': cate['cate_name'],
            'cate_remark': cate['cate_remark'],
            'desc': '',
            'price': 0,
            'old_price': 0,
            'url': ''
        }
        info_flied_arr = [x for x in info_tmp.keys()]
        getOneCatePage(cate['cate_url'], info_tmp, info_flied_arr, tmp_data_dir, record_path)



def getCateList(url_excel_path):
    cate_list = []
    url_df = pd.read_excel(url_excel_path,usecols=[0,1,4])
    url_df = url_df.dropna(axis=0,how='any')
    for index in url_df.index.values:
        cate = {
            'cate_name' :  url_df.ix[index,0],
            'cate_remark' : url_df.ix[index,1],
            'cate_url' : url_df.ix[index,2]
        }
        cate_list.append(cate)
    return cate_list



def connectToOne(dir, to_dir, out_file_name):
    excel_df = pd.DataFrame()
    for file in os.listdir(dir):
        if file.endswith('.xlsx'):
            print("file:", file)
            excel_df = excel_df.append(
                pd.read_excel(os.path.join(dir, file), dtype={'url': str}, ))
    print('开始合并')
    excel_df['currency'] = '$'
    writer = pd.ExcelWriter(os.path.join(to_dir, out_file_name), engine='xlsxwriter',
                            options={'strings_to_urls': False})

    excel_df.to_excel(writer,index=False)
    writer.close()


if __name__ == '__main__':
    url_excel_path_0 = '/home/babel/Desktop/宠物竞品爬虫.xlsx'
    base_dir_0 = '/home/babel/Desktop/PET_SCRIPY'
    site_name_0 = 'www.petco.com'

    ip_proxies_list = getIPList()

    tmp_data_dir_0,out_dir_0,record_path_0 = createDir(base_dir_0,site_name_0)

    cate_list_0 = getCateList(url_excel_path_0)
    print(cate_list_0)
    cate_list_1 = [{'cate_name': 'Dog Sweaters & Hoodies',
                    'cate_remark': '毛衣卫衣',
                    'cate_url': 'https://www.petco.com/shop/en/petcostore/category/dog/dog-apparel/dog-sweaters-hoodies'},
                   {'cate_name': 'Cat Outdoor Gear', 'cate_remark': '外出用品', 'cate_url': 'https://www.petco.com/shop/en/petcostore/category/dog/dog-apparel/dog-paw-protection'}]

    #getAllCatePage(cate_list_0,site_name_0,tmp_data_dir_0,record_path_0)

    connectToOne(tmp_data_dir_0,'/home/babel/lingtian/static_files/mkcms_dev/memo/PET_total/US',"{0}_{1}.xlsx".format(site_name_0,datetime.strftime(datetime.now(),'%Y%m%d%H%M%S')))

    info_tmp_0 = {
        'brand': site_name_0,
        'cate_name': '毛衣卫衣',
        'cate_remark': '毛衣卫衣',
        'desc': '',
        'price': 0,
        'old_price': 0,
        'url': ''
    }
    #getOneCatePageByPageNext('https://www.petco.com/shop/en/petcostore/category/dog/dog-apparel/dog-sweaters-hoodies', info_tmp_0)



