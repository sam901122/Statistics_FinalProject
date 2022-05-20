import numpy as np
import pandas as pd
import datetime as dt
import copy as cp
import scipy.stats as stats
import matplotlib.pyplot as plt

transportCnt = dict()


def add_transportCnt( date: list[ dt.datetime ], comeIn: list[ int ] ) -> None:
    # Given two list, one is the date, the other is the people into every train station
    # The data type of date should be list of datetime.datetime
    # The data type of come into station people should be list of int

    # transportCnt is global variable
    global transportCnt

    # Traverse every data, add comeIn value to that day
    for i in range( len( date ) ):
        currentDate = date[ i ]
        try:
            transportCnt[ currentDate ] += comeIn[ i ]
        except:
            transportCnt[ currentDate ] = comeIn[ i ]


def convert_date( datesList: list[ int ] ) -> list[ dt.datetime ]:
    # Given a list of date, with format : yyyymmdd
    # Convert the list into date with type of datetime.datetime

    tempDatesList = cp.deepcopy( datesList )

    for i in range( len( tempDatesList ) ):
        currentDateStr = str( tempDatesList[ i ] )
        year = int( currentDateStr[ :4 ] )
        month = int( currentDateStr[ 4:6 ] )
        day = int( currentDateStr[ 6:8 ] )
        tempDatesList[ i ] = dt.datetime( year, month, day )
    return tempDatesList


def get_trCnt():
    global transportCnt

    df_2005_to_2007 = pd.read_csv( '2005-20190422/2005-2017.csv' )
    df_2018 = pd.read_csv( '2005-20190422/2018.csv' )
    df_2019_1 = pd.read_csv( '2005-20190422/20190422.csv' )
    df_2019_2 = pd.read_csv( '20190423-20211231/20190423-20191231.csv' )
    df_2020 = pd.read_csv( '20190423-20211231/2020.csv' )
    df_2021 = pd.read_csv( '20190423-20211231/2021.csv' )
    df_2022 = pd.read_csv( '2022.csv' )

    date_2005_to_2017 = df_2005_to_2007[ 'BOARD_DATE' ]
    comeIn_2005_to_2017 = df_2005_to_2007[ '進站' ]

    date_2018 = df_2018[ 'BOARD_DATE' ]
    comeIn_2018 = df_2018[ '進站' ]

    date_2019_1 = df_2019_1[ 'BOARD_DATE' ]
    comeIn_2019_1 = df_2019_1[ '進站' ]

    date_2019_2 = df_2019_2[ 'trnOpDate' ]
    comeIn_2019_2 = df_2019_2[ 'gateInComingCnt' ]

    date_2020 = df_2020[ 'trnOpDate' ]
    comeIn_2020 = df_2020[ 'gateInComingCnt' ]

    date_2021 = df_2021[ 'trnOpDate' ]
    comeIn_2021 = df_2021[ 'gateInComingCnt' ]

    date_2022 = df_2022[ 'trnOpDate' ]
    comeIn_2022 = df_2022[ 'gateInComingCnt' ]

    datesList = list( date_2005_to_2017 )
    datesList += list( date_2018 )
    datesList += list( date_2019_1 )
    datesList += list( date_2019_2 )
    datesList += list( date_2020 )
    datesList += list( date_2021 )
    datesList += list( date_2022 )

    comeInsList = list( comeIn_2005_to_2017 )
    comeInsList += list( comeIn_2018 )
    comeInsList += list( comeIn_2019_1 )
    comeInsList += list( comeIn_2019_2 )
    comeInsList += list( comeIn_2020 )
    comeInsList += list( comeIn_2021 )
    comeInsList += list( comeIn_2022 )

    datesList = convert_date( datesList )

    add_transportCnt( datesList, comeInsList )

    return transportCnt


def get_holiday_dict():
    dict_holi_type = {}
    dict_holi_len = {}
    df_holiday = pd.read_excel( 'Holidays.xlsx' )
    for i in range( len( df_holiday ) ):
        stDate = df_holiday.iloc[ i ][ 0 ].to_pydatetime()
        Duration = df_holiday.iloc[ i ][ 1 ]
        holiType = df_holiday.iloc[ i ][ 2 ]
        currentDt = stDate

        for i in range( Duration ):
            dict_holi_len[ currentDt ] = Duration
            dict_holi_type[ currentDt ] = holiType
            currentDt = currentDt + dt.timedelta( days=1 )
    return dict_holi_type, dict_holi_len


def self_qqplot( glo_data: dict, year_split ) -> None:
    data = [ ( date, glo_data[ date ] ) for date in glo_data.keys() ]
    data = sorted( data, key=lambda i: i[ 1 ] )
    temp = []
    for date, cnt in data:
        temp.append( np.array( [ date.year, cnt ] ) )
    temp = np.array( temp )
    mean = np.mean( temp.T[ 1 ] )
    sigma = temp.T[ 1 ].std( ddof=1 )

    nd = stats.norm( mean, sigma )
    percent = 0
    single_percent = 1 / len( data )

    theo = []
    for i in range( len( data ) ):
        theo.append( nd.ppf( percent ) )
        percent += single_percent

    year = list( temp.T[ 0 ] )
    cnt = list( temp.T[ 1 ] )

    before_pair = []
    after_pair = []
    for i in range( len( year ) ):
        if year[ i ] >= year_split:
            after_pair.append( np.array( [ cnt[ i ], theo[ i ] ] ) )
        else:
            before_pair.append( np.array( [ cnt[ i ], theo[ i ] ] ) )
    before_pair = np.array( before_pair )
    after_pair = np.array( after_pair )

    fig, ax = plt.subplots( 1, 2, figsize=( 30, 10 ) )
    ax[ 0 ].scatter( before_pair.T[ 1 ], before_pair.T[ 0 ], c='b', s=2.5, alpha=0.3 )
    ax[ 1 ].scatter( after_pair.T[ 1 ], after_pair.T[ 0 ], c='r', s=2.5, alpha=0.3 )
    ax[ 0 ].plot( ax[ 0 ].get_xlim(), ax[ 0 ].get_xlim(), color="black", alpha=0.3 )
    ax[ 1 ].plot( ax[ 1 ].get_xlim(), ax[ 1 ].get_xlim(), color="black", alpha=0.3 )
