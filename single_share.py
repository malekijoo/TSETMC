#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
In this script, a process of scrapping single share file
is performed. Every share name, in main file, if fed to
the process in order to eximine in their share pages.
This process go for every share on by one. because of that,
it might take a while to complete the task.

"""
import os
import time
import getpass
import requests
import pandas as pd

from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

url = 'http://www.tsetmc.com/'
if 'posix' in os.name:
    ch_path = "/usr/local/bin/chromedriver"
elif 'nt' in os.name:
    ch_path = "C:\\Users\\{}\\Desktop\\TSETMC\\chromedriver".format(str(getpass.getuser()))

if 'posix' in os.name:
    path = '/Users/amir/Documents/CODE/Python/start/'
elif 'nt' in os.name:
    path = "C:\\Users\\{}\\Desktop\\start\\".format(str(getpass.getuser()))

"""
Functions in this section is employed to check 
different element and conditions.
"""


def check_existence_by_tag(element, tag):
    try:
        element[1].find_element_by_tag_name(tag)
    except IndexError:
        return False
    except NoSuchElementException:
        return False
    else:
        return True


def check_share_condition(soup, driver):
    """
    if check.check_share_condition(html):
    print('مجاز')
    else:
    print('متوقف-ممنوع')
    :param html:
    :return:
    """
    t = soup.find(text='وضعیت').parent.parent
    t = t.get_text()
    if len(t) == 5:
        t = driver.find_element_by_xpath('//*[@id="d01"]').text
        # time.sleep(1)
    if 'مجاز' in t:
        return True
    else:
        return False


def check_page(soup, type_):
    if type_ == 'homepage':
        if 'TSETMC' in soup.title.text:
            return True
        else:
            # print('screwed, it is not the homepage silly.')
            return False
    elif type_ == 'historypage':
        if soup.find(text='نمایش روزهای معامله شده') is not None:
            return True
        else:
            # print('screwed, it is not the history page silly.')
            return False
    elif type_ == 'sharepage':
        if soup.find(text='ابزار تغییر مکان یا نمایش اطلاعات') is not None:
            return True
        else:
            # print('screwed, it is not the share page silly.')
            return False


"""

Bellow section is dedicated to working with the share object.
In this, we use the file to retrieve the share objects.

"""
def read_share_name_from_execl(path_=path, name='shares'):
    df = pd.read_excel(path_ + name)
    df.rename(columns=df.iloc[0])
    return df['نماد'].tolist()


def find_last_data_entered_in_file(path_=path, filename='dataframe.xlsx'):

    if os.path.exists(path_ + filename):
        df = pd.read_excel(path_ + filename)
        if len(df) > 0:
            max_ = df["datetime"][0]
            for i in range(len(df.index) - 1):
                if max_ < df['datetime'][i + 1]:
                    max_ = df['datetime'][i + 1]
            dp = df.loc[df['datetime'] == max_]
            dic = dp.to_dict('list')
            # print(dic)
            return dic


def find_last_today_entry(name_, path_=path, filename='dataframe.xlsx'):
    date_ = pd.datetime.now().date()

    if os.path.exists(path_ + filename):
        df = pd.read_excel(path_ + filename)
        dff = df.loc[df['name'] == name_]
        df3 = dff[dff['datetime'].dt.date == date_]
        df4 = df3.reset_index()

        if len(df4) > 1:
            max_ = df4["datetime"][0]
            for i in range(len(df4.index) - 1):
                if max_ < df4['datetime'][i + 1]:
                    max_ = df4['datetime'][i + 1]

            dp = df.loc[df['datetime'] == max_]

            return dp.to_dict('list')

        elif len(df4) == 1:
            return df4.to_dict('list')

        else:
            return None



def find_last_data_feature(name_, path_=path, filename='dataframe.xlsx'):

    if os.path.exists(path_ + filename):
        df = pd.read_excel(path_ + filename)
        dff = df.loc[df['name'] == name_]
        dff = dff.reset_index()
        if len(dff) > 0:
            max_ = dff["datetime"][0]
            for i in range(len(dff.index) - 1):
                if max_ < dff['datetime'][i + 1]:
                    max_ = dff['datetime'][i + 1]
            dp = df.loc[df['datetime'] == max_]
            dic = dp.to_dict('list')
            return dic
        else:
            # print("there is no record !!!")
            return None


class StockShare(object):

    def __init__(self, path_=path, filename='dataframe.xlsx', **kwargs):

        self.name = kwargs.get('name')
        self.price = kwargs.get('price')
        '''قیمت دیروز'''
        self.ydp = kwargs.get('ydp')
        '''قیمت پایانی'''
        self.wp_fi = kwargs.get('wp_fi')
        self.change = kwargs.get('change')
        '''تغییر قیمت با رکورد قبلی '''
        self.change_per = kwargs.get('change_per')
        self.d_high = kwargs.get('d_high')
        self.d_low = kwargs.get('d_low')
        # self.p_high = kwargs.get('p_high')
        # self.p_low = kwargs.get('p_low')
        self.eps = kwargs.get('eps')
        self.pe = kwargs.get('pe')
        # self.g_pe = kwargs.get('g_pe')
        ''' خرید'''
        self.purchase_q = kwargs.get('purchase_q')
        ''' فروش'''
        self.sale_q = kwargs.get('sale_q')

        self.trade_amount = kwargs.get('trade_amount')
        self.trade_value = kwargs.get('trade_value')
        self.trade_volume = kwargs.get('trade_volume')
        # self.whole_volume = kwargs.get('whole_volume')
        self.tepix = kwargs.get('tepix')
        self.dollar = kwargs.get('dollar')
        self.condition = kwargs.get('condition')
        self.datetime = kwargs.get('datetime')
        self.filename = filename
        self.path_ = path_

    def __call__(self, name, today=True):
        self.today = today
        self.name = name

"""
In the below section we have class and functions that 
try to load the page. Beside them, at the end of
this section, there is a function to check the position
of some elements in the driver file.
"""


class page_loader(object):
    def __init__(self,  name, sleep_time=3, **kwargs):
        self.url_main_page = url
        self.name = name
        self.sleep = sleep_time
        self.kwargs = kwargs

    def __call__(self, name, **kwargs):
        self.name = name
        self.kwargs = kwargs

    def option(self, kwargs):
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--incognito')
        options.add_argument('--headless')
        browser = webdriver.Chrome(ch_path, options=options)
        return browser

    @property
    def shares_page(self):
        driver = self.option(self)
        driver.get(self.url_main_page)
        time.sleep(1)
        try:
            driver.find_element_by_id(id_='search').click()
        except:
            time.sleep(1)
            element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="search"]')))
            element.click()
        driver.find_element_by_id("SearchKey").send_keys(self.name)
        driver.implicitly_wait(self.sleep-1)
        time.sleep(1)
        element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="SearchResult"]/div/div[2]/table/tbody/tr[1]/td[1]/a')))
        if 'قدیمی' in element.text:
            time.sleep(1)
            element = driver.find_element_by_xpath('//*[@id="SearchResult"]/div/div[2]/table/tbody/tr[2]/td[1]/a')
            if 'قدیمی' in element.text:
                element = driver.find_element_by_xpath('//*[@id="SearchResult"]/div/div[2]/table/tbody/tr[3]/td[1]/a')
        element.click()
        time.sleep(5)
        WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located((By.XPATH, '// *[ @ id = "d02"]')))
        page_source = driver.page_source
        # try:
        return page_source, driver


def url_source(page_address=url):
    try:
        with requests.Session() as s:
            url_get = s.get(page_address, verify=False)
            time.sleep(1)
            return url_get
    except InterruptedError:
        print('Check the internet connection. Currently, the site is unreachable.')
        pass


def dollar_price():

    _url = 'http://www.tgju.org/dollar-chart'
    soup = bs(url_source(_url).content, 'lxml')
    try:
        _table = soup.find_all('td', {'class': 'nf'})
        table_content = []
        for td in _table:
            row_cell = [td.get_text()]
            table_content += row_cell
            # print(table_content)
        # print('قیمت دلار در این لحظه {} ریال است'.format(table_content[0]))
        value = table_content[0].replace(',', '')
    except IndexError:
        v = find_last_data_entered_in_file()
        value = v['price']
        # print('dollar except IndexError: ', value )
    except UnboundLocalError:
        v = find_last_data_entered_in_file()
        value = v['price']
        # print('dollar except UnboundLocalError: ', value )
    finally:
        return int(value)


def check_queue(driver, i, j):
    if len(driver.find_element_by_xpath('//*[@id="bl"]/tr[{}]/td[{}]'.format(i, j)).text) > 1:
        return True


"""

Below section, is responsible for finding the element 
across the driver. wrapping them up for building an 
object of share.

"""

Tarnama = {'BDYN': 'بازار نقدی بورس در یک نگاه',
           'SHM': 'شاخص های منتخب',
           'TDSH': 'تاثیر در شاخص',
           'FBDYN': 'بازار نقدی فرابورس در یک نگاه',
           'FTDSH': 'تاثیر در شاخص',
           }


def repair_value(value):
    """
    share.repair_value(T.trade_info()[1][1]))
    :param value:
    :return: list of float number, first item is the value of the share,
    second of is the change with yesterday value
    and the last one is the percent of this change.
    """
    value = value.replace(',', '')
    value = value.replace('(', '')
    value = value.replace(')', '')
    value = value.replace('%', '')
    return list(map(float, value.split()))


def rm_comma(table_content):
    """
    remove comma from a list
    print(share.rm_comma(T.trade_info()[5]))
    :param table_content:
    :param value:
    :return: a list with out comma

    """
    for i in range(len(table_content)):
        table_content[i] = table_content[i].replace(',', '')
        try:
            table_content[i] = list(map(float, table_content[i].split()))
        except ValueError:
            pass
    return table_content


def mb_translator(entry):
    if 'M' in entry:
        entry = float(entry.split()[0]) * 1000000
    elif 'B' in entry:
        entry = float(entry.split()[0]) * 1000000000
    else:
        entry = float(entry)
    return entry


class Info:
    def __init__(self, soup, driver=None, source=None):
        self.soup = soup
        self.source = source
        self.driver = driver
        # print('initializing the info class by " {} " page'.format(self.soup.title.text))

    def __call__(self, soup, source=None):
        self.soup = soup
        self.source = source
        # print('calling the info class by " {} " page'.format(self.soup.title.text))

    def homepage_table(self, table_name):
        """
        must be home page
        to do : check page

        :return: a raw information list
        """
        source = self.soup.find(text=table_name)
        source_soup = source.parent.parent
        rows = source_soup.find_all("tr")
        table_contents = []
        for tr in rows:
            if rows.index(tr) == 0:
                row_cells = [th.getText().strip() for th in tr.find_all('th') if th.getText().strip() != '']
            else:
                row_cells = ([tr.find('th').getText()] if tr.find('th') else []) + [td.getText().strip() for td in
                                                                                    tr.find_all('td') if
                                                                                    td.getText().strip() != '']
            if len(row_cells) > 1:
                table_contents += [row_cells]

        return table_contents

    @property
    def trade_amount(self):
        """
        must be share page

        to do : check page

        instance
        response = urllib.request.urlopen('file:///Users/amir/Documents/CODE/Python/TSETMC/فملي 4,480.htm', timeout=1)
        html = response.read()
        soup = bs(html, 'html.parser')
        T = share.info(html)
        # print(T.trade_amount())
        print(T.trade_info()[0])

        :return a raw information list:
        """
        check_page(self.soup, 'sharepage')
        sale_q = 0
        purchase_q = 0
        purchase_ = 2
        sale_ = 5
        try:
            pt = self.driver.find_element_by_xpath('//*[@id="bl"]/tr[2]/td[1]').text.replace(',', '')
            if len(pt) > 0:
                pa = self.driver.find_element_by_xpath('//*[@id="bl"]/tr[2]/td[2]').text.replace(',', '')
                purchase_q += float(pa)

            st = self.driver.find_element_by_xpath('//*[@id="bl"]/tr[2]/td[6]').text.replace(',', '')
            if len(st) > 0:
                sa = self.driver.find_element_by_xpath('//*[@id="bl"]/tr[2]/td[5]').text.replace(',', '')
                sale_q += float(sa)
        except:
            try:
                trade = self.soup.find('tbody', {'id': 'bl'})
                amount_rows = trade.find_all("tr")
                for i in range(2, 5):

                    tr = amount_rows[i - 1].find_all('td')
                    if len(amount_rows[i - 1].get_text()) > 1:
                        if check_queue(self.driver, i, purchase_):

                            m = tr[1].get_text().replace(',', '')
                            purchase_q += float(m)

                        if check_queue(self.driver, i, sale_):

                            m = tr[4].get_text().replace(',', '')
                            sale_q += float(m)
            except:
                sale_q = 0
                purchase_q = 0
        return purchase_q, sale_q

    @property
    def trade_info(self):
        """
        must be share page
        to do : check page
        :return:
        """
        check_page(self.soup, 'sharepage')
        trade = self.soup.find_all('div', {'class': 'box6 h80'})
        table_contents = []
        for i in range(len(trade)):
            rows = trade[i].find_all("tr")
            for tr in rows:
                row_cells = ([tr.find('th').getText()] if tr.find('th') else []) + [td.getText().strip() for td in
                                                                                    tr.find_all('td') if
                                                                                    td.getText().strip() != '']
                if len(row_cells) > 1:
                    table_contents += [row_cells]
        # print(table_contents)
        return table_contents

    def share_value(self):
        day_price = {'high': None, 'low': None}
        # permissive = {'high': None, 'low': None}
        first_price = None

        try:
            table_contents = self.trade_info
            # print(table_contents)
            if check_share_condition(self.soup, self.driver):
                price = repair_value(table_contents[1][1])[0]
                wp_fi = repair_value(table_contents[3][1])[0]
                ydp = repair_value(table_contents[3][2])[0]
                first_price = repair_value(table_contents[3][0])[0]
                condition = 'مجاز'
            else:
                price = rm_comma(table_contents[1])[1][0]
                temp = rm_comma(table_contents[3])

                condition = 'متوقف'
                wp_fi = temp[1][0]
                ydp = temp[2][0]
                first_price = 0.0

            rm_temp = rm_comma(table_contents[5])
            # permissive = {'high': rm_temp[1][0], 'low': rm_temp[2][0]}
            day_price = {'high': rm_comma(table_contents[4])[1][0], 'low': rm_comma(table_contents[4])[2][0]}

        except (IndexError, AttributeError, ValueError):
            if self.driver.find_element_by_xpath('//*[@id="d02"]').text.count(' ') > 1:
                f = repair_value(self.driver.find_element_by_xpath('//*[@id="d02"]').text)
                price = f[0]
            else:
                f = self.driver.find_element_by_xpath('//*[@id="d02"]').text.replace(',', '')
                # print(f)
                price = float(f)
            ydp = float(self.driver.find_element_by_xpath('//*[@id="d05"]').text.replace(',', ''))

            day_price['high'] = self.driver.find_element_by_xpath('//*[@id="d06"]').text.replace(',', '')
            day_price['low'] = self.driver.find_element_by_xpath('//*[@id="d07"]').text.replace(',', '')

            if self.driver.find_element_by_xpath('//*[@id="d03"]').text.count(' ') >= 2:
                r = self.driver.find_element_by_xpath('//*[@id="d03"]').text.replace(',', '')
                wp_fi = float(r.split()[0])
            else:
                r = self.driver.find_element_by_xpath('//*[@id="d03"]').text.replace(',', '')
                wp_fi = float(r)
            condition = 'متوقف'
            if check_share_condition(self.soup, self.driver):
                condition = 'مجاز'

        trade_amount = mb_translator(self.driver.find_element_by_xpath('//*[@id="d08"]').text.replace(',', ''))
        trade_volume = mb_translator(self.driver.find_element_by_xpath('//*[@id="d09"]').text.replace(',', ''))
        trade_value = mb_translator(self.driver.find_element_by_xpath('//*[@id="d10"]').text.replace(',', ''))

        dic = {'price': price,
               'ydp': ydp,
               'first_price': first_price,
               'day_price': day_price,
               'wp_fi': wp_fi,
               'trade_volume': trade_volume,
               'trade_value': trade_value,
               'trade_amount': trade_amount,
               'condition': condition}
        return dic

    def eps_pe(self):
        """
        share page
        :return: jkdfngj
        """
        eps = self.soup.find_all(text='EPS')
        eps_ = eps[1].parent.parent.parent

        f = eps_.find_all('td')
        table_contents = []

        for i in range(len(f)):
            if f[i].get_text().strip() != '':
                row_cells = [f[i].get_text()]
                table_contents += [row_cells]

        try:
            dic = {'eps': table_contents[1][0], 'pe': table_contents[4][0], 'g_pe': table_contents[6][0]}
        except IndexError:
            m = self.driver.find_element_by_xpath('//*[@id="d03"]').text.replace(',', '')
            if m.count(' ') > 1:
                m = repair_value(m)[0]
            try:
                gpe = self.driver.find_element_by_xpath('//*[@id="TopBox"]/div[2]/div[6]/table/tbody/tr[2]/td[4]').text.replace(',', '')
                if len(gpe) < 1:
                    gpe = '0'

            except:
                gpe = '0'

            try:
                dic = {'eps': table_contents[1][0], 'pe': float(m) / float(table_contents[1][0]), 'g_pe': gpe}

            except ValueError:
                try:
                    eeps = self.driver.find_element_by_xpath('//*[@id="TopBox"]/div[2]/div[6]/table/tbody/tr[1]/td[2]').text.replace(',', '')
                except:
                    eeps = self.driver.find_element_by_xpath('//*[@id="TopBox"]/div[3]/div[6]/table/tbody/tr[1]/td[2]').text.replace(',', '')

                try:
                    dic = {'eps': eeps, 'pe': float(m) / float(eeps), 'g_pe': gpe}
                except:
                    dic = {'eps': 0, 'pe': 0, 'g_pe': 0}

        return dic

    @property
    def data_history(self):
        """
        must be on sabeghe page
        to do : check page
        :return:
        """
        check_page(self.soup, 'historypage')

        table = self.soup.find('table', {'class': 'obj row20px'})

        rows = table.find_all("tr")
        table_contents = []
        for tr in rows:
            row_cells = [td.getText().strip() for td in tr.find_all('td') if td.getText().strip() != '']
            table_contents += [row_cells]

        return list(filter(None, table_contents))


def get_name(soup, driver):
    sh_name = soup.title.get_text()
    name_ = sh_name.split(" ")[0]
    if 'TSETMC' in name_:
        s = driver.find_element_by_xpath('//*[@id="MainBox"]/div[1]').text
        name_ = s[s.find('(') + 1:s.find(')')]
    return name_


def tepixx(homepage, driver, name):

    inf1 = Info(homepage)
    z = inf1.homepage_table(Tarnama.get('BDYN'))
    temp = rm_comma(z[0][1].split(' '))
    tepix_ = temp[0][0]
    if float(tepix_) < 100:
        tepix_ = 0
        try:
            # time.sleep(1)
            te = driver.find_element_by_xpath('//*[@id="FastView"]/span[1]')
            temp1 = te.text.split()
            tepix_ = temp1[0].split(':')[1]
            tepix_ = rm_comma(tepix_)
        except:
            element = find_last_today_entry(name_=name)
            if element is not None:
                tepix_ = element['tepix'][0]
    return tepix_


def making_data_prepared(soup, homepage, usd, sh_driver):

    inf = Info(soup, driver=sh_driver)
    sh_name = get_name(soup, sh_driver)
    purchase_q, sale_q = inf.trade_amount
    eps_ = inf.eps_pe()
    sh_dic = inf.share_value()
    try:
        tepix = tepixx(homepage, sh_driver, sh_name)
    except:
        pass
    element = find_last_today_entry(name_=sh_name)
    try:
        if element is None or not element['price']:
            change = sh_dic['price'] - sh_dic['ydp']
            # change_per = change / sh_dic['ydp']
            change_per = round((change / sh_dic['ydp']) * 100, 2)


        else:
            last_price = element['price'][0]
            change = sh_dic['price'] - last_price
            change_per = round((change / last_price) * 100, 2)
    except TypeError:
        if element is None or not element['price']:
            if sh_driver.find_element_by_xpath('//*[@id="d02"]').text.count(' ') > 1:
                kk = repair_value(sh_driver.find_element_by_xpath('//*[@id="d02"]').text)
                jj = sh_driver.find_element_by_xpath('//*[@id="d05"]').text
                jj = float(jj.replace(',', ''))
            else:
                kk = sh_driver.find_element_by_xpath('//*[@id="d02"]').text.replace(',', '')
                jj = sh_driver.find_element_by_xpath('//*[@id="d05"]').text
                jj = float(jj.replace(',', ''))
            change = float(kk) - jj
            # change_per = change / jj
            change_per = round((change / jj) * 100, 2)

        else:
            last_price = element['price'][0]
            if sh_driver.find_element_by_xpath('//*[@id="d02"]').text.count(' ') > 1:
                kk = repair_value(sh_driver.find_element_by_xpath('//*[@id="d02"]').text)
            else:
                kk = rm_comma(sh_driver.find_element_by_xpath('//*[@id="d02"]').text)
            change = kk - last_price
            change_per = round((change / last_price) * 100, 2)

    dic = {'name': sh_name,
           'price': sh_dic['price'],
           'wp_fi': sh_dic['wp_fi'],
           'ydp': sh_dic['ydp'],
           'change': change,
           'tepix': tepix,
           'change_per': change_per,
           # 'whole_volume': sh_dic['whole_volume'],
           'trade_volume': sh_dic['trade_volume'],
           'trade_value': sh_dic['trade_value'],
           'trade_amount': sh_dic['trade_amount'],
           'eps': float(eps_['eps']),
           'pe': float(eps_['pe']),
           'g_pe': float(eps_['g_pe']),
           'dollar': usd,
           'd_low': float(sh_dic['day_price']['low']),
           'd_high': float(sh_dic['day_price']['high']),
           # 'p_low': float(sh_dic['permissive_price']['low']),
           # 'p_high': float(sh_dic['permissive_price']['high']),
           'purchase_q': purchase_q,
           'sale_q': sale_q,
           'condition': sh_dic['condition'],
           'datetime': pd.datetime.now()
           }
    return dic
