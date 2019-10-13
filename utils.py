import os
import time
import getpass
from selenium import webdriver
from bs4 import BeautifulSoup as bs


if 'posix' in os.name:
    ch_path = "/usr/local/bin/chromedriver"
elif 'nt' in os.name:
    ch_path = "C:\\Users\\{}\\Desktop\\TSETMC\\chromedriver".format(str(getpass.getuser()))


def fix_v(value, other=False, dot=False):
    """
    share.fix_v(T.trade_info()[1][1]))

    :param other: if True, the "()%:" will be removed
    :param dot: if True, the dot will be removed

    :param value: value is editing here
    :return: list of float number, first item is the value of the share,
    second of is the change with yesterday value
    and the last one is the percent of this change.

    """
    value = value.replace(',', '')
    if other:
        value = value.replace('(', ' ')
        value = value.replace('-', ' ')
        value = value.replace(')', ' ')
        value = value.replace('%', '')
        value = value.replace(':', ' ')
    if dot:
        value = value.replace('.', '')
    # value = value.split(' ')
    # list(map(float, value.split()))
    return value


def mb_trans(val):
    """
    :return: entry which is changed
    :param val: the value which should be change

    """
    val = fix_v(val)

    if 'M' in val:
        val = val.replace('M', '')
        val = float(val) * 1000000
    elif 'B' in val:
        val = val.replace('B', '')
        val = float(val) * 1000000000
    else:
        val = float(val)

    return val


def rm_(value):

    if '-' in value:
        value = 0.0
    else:
        value = float(fix_v(value))
    return value


class Loader:
    """

    this class loads the page with specific setting
    :parameter url, name. we get the address of the website and verify the page
               with the name.
    :returns page_source, driver. page_source is fed to Beautifulsoup function.
             the driver is passed to other function to be exploited by other functions.

    """
    @staticmethod
    def option():

        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--incognito')
        options.add_argument('--headless')
        browser = webdriver.Chrome(ch_path, options=options)

        return browser

    @classmethod
    def page(cls, url, name_, slp_):

        driver = cls.option()
        driver.get(url)
        driver.implicitly_wait(10)
        time.sleep(slp_)
        assert name_ in driver.title
        page_source = driver.page_source
        # driver.close()
        return page_source, driver


def load(address, name_, slp=5):

    for i in range(1, 6):
        try:
            page, driver = Loader.page(url=address, name_=name_, slp_=slp)
            print("the page '{}' is loaded now...".format(name_))
            # print('{} st/nd/rd/th try was successful and hit the site. the loop ends now'.format(i))
            break
        except:
            print(' {} retrying........'.format(i))

    soup = bs(page, 'html.parser')

    return driver, soup
