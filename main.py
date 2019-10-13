import extractor
import utils as ut
import datetime as dt


__version__ = "3.2.2"
print(" current version is  '{}'.".format(__version__))

# address = 'http://www.tsetmc.com/Loader.aspx?ParTree=15131F'



def process():

    time_ = dt.datetime.now()
    name = 'بازار'
    address = 'http://www.tsetmc.com/Loader.aspx?ParTree=15131F'
    driver, soup = ut.load(address, name)
    list_of_share_name = extractor.bunch_(driver, soup)

    print('***       examining the dide-ban bazar is finished in this loop          ***')

    extractor.single(list_of_share_name)

    print('***       the list of share is empty now. this loop is finished now.     ***')
    print('          This round start at {} and took {} time.'.format(time_, dt.datetime.now() - time_))
    print('***             ************ ************ ************                   ***')


if __name__ == "__main__":

    print("let's go,  {}".format(dt.datetime.now()))
    if dt.datetime.now().hour > 7:
        start_time = dt.datetime.now()
        print('the market is open now. we start at {}'.format(start_time))
        while dt.datetime.now().hour < 20:
            process()
        print('we start sampling at {} and finish at {}.'.format(start_time, dt.datetime.now()))
    else:
        print("today's span was finished, plz comeback tomorrow at sharp 9.")

