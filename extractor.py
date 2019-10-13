"""
There are two methods used in this file.
First one, bunch_ ,is used to hit the 'Dide-ban Bazar'
of TSETMC in order to scrape information

"""

import os
import time
import datum
import getpass
import store as st
import pandas as pd
import single_share as owss

from tqdm import tqdm
from bs4 import BeautifulSoup as bs
from selenium.common import exceptions


if 'posix' in os.name:
    path = "/Users/amir/Documents/CODE/Python/start/"
elif 'nt' in os.name:
    path = "C:\\Users\\{}\\Desktop\\start\\".format(str(getpass.getuser()))


def read_share_name_from_execl(pathe=path, name='shares.xlsx'):
    df = pd.read_excel(pathe + name)
    df.rename(columns=df.iloc[0])
    return df['نماد'].tolist()


def check_and_store(obj):

    last_rec = owss.find_last_data_feature(name_=obj.name)
    last_rec_price = 0
    if last_rec is not None:
        last_rec_price = last_rec['price'][0]
    if obj.price != last_rec_price:
        st.write_to_execl(obj)


def bunch_(driver, soup):

    shares_names = read_share_name_from_execl()
    instance = datum.Information(driver, soup)
    instance.info()

    bunch_element = driver.find_element_by_xpath('//*[@id="main"]')
    line_elements = bunch_element.find_elements_by_tag_name('div')

    pbar = tqdm(line_elements, ncols=100)
    pbar.write("Processing the 'Dide-ban Bazar' page")
    for i, ele in enumerate(pbar, 0):
        try:
            if len(line_elements[i].text) > 41:
                data = line_elements[i].find_elements_by_tag_name('div')
                data = list(map(lambda x: x.text, data))
                if data[0] in shares_names:
                    instance.info_share(data)
                    check_and_store(instance)
                    shares_names.remove(data[0])
        except exceptions.StaleElementReferenceException as e:
            print(e)
            pass
    print(" '{}' share successfully saved in dataframe.".format(instance.counter()))
    return shares_names


def single(sh_list):

    homepage = bs(owss.url_source().content, 'lxml')
    usd = owss.dollar_price()
    next_phase = []
    loop_ = 1

    while True:

        if 1 < loop_ < 5 and len(sh_list) != 0:
            sh_list = next_phase
        next_phase = []
        pbar = tqdm(sh_list, ncols=100)
        pbar.write("Processing the list of share which is not in the original page. \n")
        for ii, _ in enumerate(pbar, 0):
            time_temp = pd.datetime.now()
            min_ = time_temp.minute
            sec_ = time_temp.second
            if min_ % 10 == 0 and sec_ < 17:
                homepage = bs(owss.url_source().content, 'lxml')
                usd = owss.dollar_price()

            name = sh_list[ii]
            try:
                page = owss.page_loader(name)
                html, sh_driver = page.shares_page
                soup = bs(html, 'html.parser')
                time.sleep(1)
                if not owss.check_share_condition(soup, sh_driver):
                    print('this share ({}) is stopped for some reason.'.format(name))

                df = owss.making_data_prepared(soup, homepage, usd, sh_driver)
                # print(df)
                share = owss.StockShare(**df)
                check_and_store(share)

            except:
                # print("the share ({}) did not respond currently, we will back to it in next phase.".format(name))
                next_phase.append(name)

        loop_ += 1
        if len(next_phase) == 0:
            print('***          the list of single share is now covered.         ***')
            break

