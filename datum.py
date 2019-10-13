"""

This file is dedicated to build a share object.
The class of Information produces different information
about shares in order to save in datafram.


"""
import utils as ut
import pandas as pd


c_book = {'tepix': 'شاخص'}


class Information(object):
    page_name = None
    name = None
    price = None
    ydp = None
    wp_fi = None
    change = None
    change_per = None
    d_high = None
    d_low = None
    p_high = None
    p_low = None
    eps = None
    pe = None
    whole_volume = None,
    trade_volume = None,
    trade_value = None,
    trade_amount = None,
    g_pe = None,
    tepix = None,
    dollar = None,
    purchase_q = None,
    sale_q = None,
    condition = None,
    datetime = None

    data_count = 0

    def __init__(self, driver, soup):
        self.soup = soup
        self.driver = driver
        print(' initializing the page .....')

    def __call__(self, driver, name, soup=None):
        self.soup = soup
        self.driver = driver
        print(' calling another page with name  ', name)

    @property
    def get_name(self):
        sh_name = self.soup.title.get_text()
        return sh_name.split(" ")[4]


    @property
    def get_tepix(self):
        a = self.driver.find_element_by_xpath('//*[@id="FastView"]/span[1]').text.split(' ')
        b = [i for i, e in enumerate(a) if c_book['tepix'] in e][0]
        list_tp = ut.fix_v(a[b])
        try:
            c = list_tp.split(':')[1]
        except:
            c = [i for i, e in enumerate(list_tp) if c_book['tepix'] not in e]
        return float(ut.fix_v(c))


    @staticmethod
    def dollar_price():
        _url = 'http://www.tgju.org/dollar-chart'
        _, _soup = ut.load(_url, 'دلار')
        _table = _soup.find_all('td', {'class': 'nf'})
        table_content = []
        for td in _table:
            row_cell = [td.get_text()]
            table_content += row_cell
            # print(table_content)
        print(" dollar's Price is  {}  now".format(table_content[0]))
        value = table_content[0].replace(',', '')
        return int(value)

    """
    These two below class function are really important.
    They try to construct the data structure.
    """

    def info(self):
        self.page_name = self.get_name
        self.tepix = self.get_tepix
        self.dollar = self.dollar_price()

    def info_share(self, dt):

        self.name = dt[0]
        self.price = float(ut.fix_v(dt[8]))
        self.ydp = float(ut.fix_v(dt[6]))
        self.wp_fi = float(ut.fix_v(dt[11]))
        self.change = float(ut.fix_v(dt[9]))
        self.change_per = float(dt[10])
        self.d_high = float(ut.fix_v(dt[15]))
        self.d_low = float(ut.fix_v(dt[14]))
        self.eps = ut.rm_(dt[16])
        self.pe = ut.rm_(dt[17])
        self.trade_amount = float(ut.fix_v(dt[2]))
        self.trade_volume = ut.mb_trans(dt[3])
        self.trade_value = ut.mb_trans(dt[4])
        self.purchase_q = float(ut.mb_trans(dt[19]))
        self.sale_q = float(ut.mb_trans(dt[23]))
        self.condition = 'مجاز'
        self.datetime = pd.datetime.now()

        self.data_count += 1

    @classmethod
    def counter(cls):
        # print('total number of data which is save in this run is  ', cls.data_count)
        return cls.data_count

