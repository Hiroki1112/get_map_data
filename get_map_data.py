#!/usr/bin/env python3
# get_map_data.py googleマップから店舗情報などを取得：WordPressに張り付けることができるフォーマットにするプログラム
import time,sys,requests,bs4,re,pyperclip
import chromedriver_binary
from selenium import webdriver
from bs4 import BeautifulSoup

Path = "./choromedriver.exe"

if __name__ == "__main__":

    #検索蘭にキーワードを記入
    file = input("保存ファイル名")
    keys = input("検索キーワード(,区切りで複数指定可能)：")
    keys = keys.split(",")

    #Google Chromeのドライバを用意
    driver = webdriver.Chrome(executable_path=Path)

    with open(file, mode='x') as f:
        f.write("  \n")

    week = ["月","火","水","木","金","土","日"]

    for key in keys:
        adress = ''
        phone = ''
        web = ''
        workday = ''
        holiday = ''
        #Google mapsを開く
        url = 'https://www.google.co.jp/maps/'
        driver.get(url)

        time.sleep(5)

        #データ入力
        id = driver.find_element_by_id("searchboxinput")
        id.send_keys(key)

        time.sleep(1)

        #クリック
        search_button = driver.find_element_by_xpath("//*[@id='searchbox-searchbutton']")
        search_button.click()

        time.sleep(3)

        try:
            #複数の候補があった場合
            login_button = driver.find_element_by_class_name("section-result-title")
            login_button.click()

        except:
            a = 1
            #print("no other target")

        time.sleep(3)

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        title = soup.find(class_="section-hero-header-title-title GLOBAL__gm2-headline-5")
        info = soup.find_all(class_="ugiz4pqJLAG__primary-text gm2-body-2")
        phone_pattern = r'[\(]{0,1}[0-9]{2,4}[\)\-\(]{0,1}[0-9]{2,4}[\)\-]{0,1}[0-9]{3,4}'

        for i in info:
            if '〒' in i.text:
                adress += i.text
            elif re.match(phone_pattern, i.text) != None:
                phone += i.text
            elif ".jp" in i.text or ".net" in i.text or ".com" in i.text:
                web = i.text
                try:
                    if requests.get('http://' + web).status_code == 200:
                        web = 'http://' + web
                except:
                    try:
                        if requests.get('https://' + web).status_code == 200:
                            web = 'https://' + web
                    except:
                        try:
                            if requests.get('http://www.' + web).status_code == 200:
                                web = 'http://www.' + web
                        except:
                            try:
                                if requests.get('https://www.' + web).status_code == 200:
                                    web = 'https://www.' + web
                            except:
                                web =''
                        
        #定休日などの情報
        time.sleep(5)
        
        try:
            elm = driver.find_element_by_class_name("cX2WmPgCkHi__primary-text")
            elm.click()
            elmok = True
        except:
            print("{}：営業情報無し".format(key))
            elmok = False
        
        time.sleep(1)
        
        if elmok:
            weeklyOpen = driver.find_elements_by_class_name("lo7U087hsMA__row-row")

            #開店時間の探索
            tmp = []
            for i in weeklyOpen:
                if i.text == " " or i.text == "\n" or i.text=="":
                    continue
                if '定休日' not in i.text:
                    tmp.append(i.text.split("\n")[1])

            if len(list(set(tmp))) == 1:
                if list(set(tmp))[0] != "24 時間営業":
                    workday = list(set(tmp))[0].replace("時",":").replace("分","")
                else:
                    workday = list(set(tmp))[0]
                
            else:
                for i in list(set(tmp)):
                    t = []
                    for j in weeklyOpen:
                        if j.text == " " or j.text == "\n":
                            continue
                        elif j.text.split("\n")[1] == i:
                            t.append(str(j.text.split("\n")[0]).replace("曜日",""))
                            
                    t = sorted(t, key=week.index)
                    workday = ",".join(t) + "曜日 " + i.replace("時",":").replace("分","") + ","
                
                workday = workday[:-1]
            
            
            #汚いアルゴリズムだが、愚直に探索する。
            #定休日探索
            holist = []
            for i in weeklyOpen:
                if '定休日' in i.text:
                    holist.append(str(i.text.split("\n")[0]).replace("曜日",""))
            
            holist = sorted(holist, key=week.index)
            if len(holist) != 0:
                holiday = ",".join(holist) + "曜日"
        
        
        li = [adress,phone,web,workday,holiday]
        out = ""
        for i,pre in zip(li,["住所：","電話番号：","Web：","営業時間：","定休日："]):
            if i=="":
                continue
            elif pre == "Web：":
                out += pre + '<a href="{}" target="_blank" rel="noreferrer noopener">{}</a>'.format(i,i) + "<br>\n"
            else:
                out += pre + str(i)+"<br>\n"
        
        infobox = '<!-- wp:cocoon-blocks/info-box --><div class="wp-block-cocoon-blocks-info-box primary-box block-box">'
        center = '<div style="display: flex; justify-content: center;">'
        paras = "<!-- wp:paragraph -->"
        parae = "<!-- /wp:paragraph -->"
        htmls = "<!-- wp:html -->"
        htmle = "<!-- /wp:html --></div><!-- /wp:cocoon-blocks/info-box -->"

        #マップ情報をコピー
        result = ""
        try:
            map1 = driver.find_element_by_xpath('//*[@id="pane"]/div/div[1]/div/div/div[5]/div[5]/div/button').click()
            time.sleep(3.5)
            umekomi = driver.find_element_by_xpath('//*[@id="modal-dialog-widget"]/div[2]/div/div[3]/div/div/div[1]/div[2]/button[2]').click()
            time.sleep(3.5)
            html = driver.find_element_by_xpath('//*[@id="modal-dialog-widget"]/div[2]/div/div[3]/div/div/div/div[3]/div[1]/button[2]').click()
            time.sleep(0.5)
            maphtml = pyperclip.paste()
            result = infobox + paras + "<p>\n" + out + "</p>\n" + parae + htmls + center + maphtml + "\n</div>\n" + htmle
        
        except:
            print(sys.exc_info())
            print("{}：map copyでエラー".format(key))
        
        with open(file, mode='a') as f:
            if title == None:
                f.write("<h2/>" + key + "</h2>\n" + '<!-- wp:html -->\n<div style="display: flex; justify-content: center;">\n\n</div>\n<!-- /wp:html --><!-- wp:paragraph --><p></p><!-- /wp:paragraph -->\n')
            else:
                f.write("<h2/>" + title.text + "</h2>\n" + '<!-- wp:html -->\n<div style="display: flex; justify-content: center;">\n\n</div>\n<!-- /wp:html --><!-- wp:paragraph --><p></p><!-- /wp:paragraph -->\n')
            f.write(result)
            f.write("\n\n")