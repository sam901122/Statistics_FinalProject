from cmath import phase, sin
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


def self_qqplot( glo_data: dict, year_split=20000 ) -> None:
    dates = []
    cnts = []
    for key in glo_data.keys():
        dates.append( key )
        cnts.append( glo_data[ key ] )

    cnts, dates = [ np.array( i ) for i in zip( *sorted( zip( cnts, dates ) ) ) ]

    mean = np.mean( cnts )
    std = cnts.std( ddof=1 )
    nd = stats.norm( mean, std )

    single_percent = 1 / len( dates )
    percent = single_percent

    theos = []
    for i in range( len( dates ) ):
        theos.append( nd.ppf( percent ) )
        percent += single_percent
    theos = np.array( theos )

    before_pair = { 'cnt': [], 'theo': [] }
    after_pair = { 'cnt': [], 'theo': [] }

    for i in range( len( dates ) ):
        if dates[ i ].year >= year_split:
            after_pair[ 'cnt' ].append( cnts[ i ] )
            after_pair[ 'theo' ].append( theos[ i ] )
        else:
            before_pair[ 'cnt' ].append( cnts[ i ] )
            before_pair[ 'theo' ].append( theos[ i ] )

    fig = plt.figure( figsize=( 20, 10 ) )
    ax1 = fig.add_subplot( 2, 1, 1 )
    ax2 = fig.add_subplot( 2, 1, 2, sharex=ax1, sharey=ax1 )
    ax1.scatter( before_pair[ 'theo' ], before_pair[ 'cnt' ], c='b', s=2.5, alpha=0.1 )
    ax1.plot( ax1.get_xlim(), ax1.get_xlim(), color="black", alpha=0.3 )
    if ( len( after_pair[ 'cnt' ] ) > 0 ):
        ax2.scatter( after_pair[ 'theo' ], after_pair[ 'cnt' ], c='r', s=2.5, alpha=0.1 )
        ax2.plot( ax2.get_xlim(), ax2.get_xlim(), color="black", alpha=0.3 )

    # Outlier dict
    dif = abs( theos - cnts )
    dif, dates, cnts, theos = [ np.array( i ) for i in zip( *sorted( zip( dif, dates, cnts, theos ), reverse=True ) ) ]
    return dif, dates, cnts, theos


def gen_ANOVA_xlsx():
    holi_dict_type, holi_dict_len = get_holiday_dict()
    typhoon_date = pd.read_excel( 'Typhoon_date.xlsx' )[ '日期' ]
    typhoon_date = [ date.to_pydatetime() for date in typhoon_date ]
    transCnt_dict = get_trCnt()
    metroCnt_dict = {}
    df_MRT = pd.read_excel( 'Metro.xlsx' )
    mrtCnt = df_MRT[ 'Metro' ]
    for i in range( len( mrtCnt ) ):
        metroCnt_dict[ df_MRT[ 'date' ][ i ].to_pydatetime() ] = mrtCnt[ i ]

    # Set
    TRADI = [ '春節', '端午', '中秋' ]
    NATION = [ '雙十', '二二八', '元旦', '清明', '勞動' ]

    mrtIndex = 0
    # List
    dates = []
    years = []
    months = []
    days = []
    weekdays = []
    trans_cnts = []
    mrt_cnts = []
    is_typhoons = []
    is_workings = []
    day_types = []
    is_foreigns = []
    holi_types = []
    holi_lens = []
    is_CNYEs = []
    is_NYEs = []
    belongs = []
    '''
    date -> datetime()
    year -> int, year of the date 
    month -> int, month of the date 
    day -> int, day of the date 
    weekday -> int, [0,6] the weekday of the date 
    trans_cnt -> int, the transport cnt of the date 
    is_typhoon -> bool, is typhoon that date 
    is_working -> bool, whether the days need to work 
    day_type -> str, 'traditional', 'national', 'weekdend', 'weekday'
    is_foreign -> bool, is the date a foreign holiday 
    holi_type -> str, the type of the holiday 
    holi_lens -> int, the length of the not working day 
    phase -> str, 'start', 'mid', 'end'
    is_NYE -> bool, is new year eve 
    belong -> which holiday ( or weekend ) the day belong to
    '''

    # Build table
    for key in transCnt_dict.keys():
        # dates
        dates.append( key )

        # year
        years.append( key.year )

        # mrt
        try:
            mrt_cnts.append( metroCnt_dict[ key ] )
        except:
            mrt_cnts.append( 0 )

        # month
        months.append( key.month )

        # day
        days.append( key.day )

        # weekday
        weekdays.append( key.weekday() )

        # trans_cnt
        trans_cnts.append( transCnt_dict[ key ] )

        # is_typhoon
        is_typhoons.append( key in typhoon_date )

        # is_working
        if ( weekdays[ -1 ] in range( 0, 5 ) ) and ( key not in holi_dict_type.keys() ):
            is_workings.append( True )
        else:
            is_workings.append( False )

        # day_type
        if key in holi_dict_type.keys():
            if holi_dict_type[ key ] in TRADI:
                day_types.append( 'Traditional' )
            elif holi_dict_type[ key ] in NATION:
                day_types.append( 'National' )
        else:
            if key.weekday() in range( 0, 5 ):
                day_types.append( 'weekday' )
            else:
                day_types.append( 'weekend' )

        # is_foreign
        if ( key.month ) == 2 and ( key.day == 14 ):
            is_foreigns.append( True )
        elif ( key.month == 10 ) and ( key.day == 31 ):
            is_foreigns.append( True )
        elif ( key.month == 12 ) and ( key.day == 25 ):
            is_foreigns.append( True )
        else:
            is_foreigns.append( False )

        # holi_type
        if key in holi_dict_type.keys():
            holi_types.append( holi_dict_type[ key ] )
        else:
            holi_types.append( 'None' )
        '''
        # is_CNYE
        if key not in holi_dict_type.keys():
            is_CNYEs.append( False )
        else:
            if holi_dict_type[ key ] == '春節':
                try:
                    if holi_dict_type[ key + dt.timedelta( days=-1 ) ] == '春節':
                        is_CNYEs.append( False )
                except:
                    is_CNYEs.append( True )
            else:
                is_CNYEs.append( False )
        '''

        # is_NYE
        if key.month == 12 and key.day == 31:
            is_NYEs.append( True )
        else:
            is_NYEs.append( False )

    holi_lens = [ 0 ] * len( holi_types )
    phase = [ 'None' ] * len( holi_types )
    belongs = [ 'None' ] * len( holi_types )

    # holi_len & phase & belong
    startIndex = -1
    duration = 0
    for i in range( len( holi_types ) ):
        if ( startIndex == -1 ) and ( is_workings[ i ] == False ):
            startIndex = i
            duration = 0
        if ( startIndex != -1 ) and ( is_workings[ i ] == True ):
            for j in range( startIndex, i ):
                holi_lens[ j ] = min( duration, 5 )
                belongs[ j ] = day_types[ startIndex ]
            belongs[ startIndex - 1 ] = day_types[ startIndex ]

            if duration >= 3:
                phase[ startIndex - 1 ] = 'start'
                phase[ startIndex ] = 'start'
                for j in range( startIndex + 1, i - 1 ):
                    phase[ j ] = 'mid'
                phase[ i - 1 ] = 'end'

            elif duration == 2:
                phase[ startIndex - 1 ] = 'start'
                phase[ startIndex ] = 'mid'
                phase[ i - 1 ] = 'end'

            startIndex = -1
        duration += 1
    '''
    date -> datetime()
    year -> int, year of the date 
    month -> int, month of the date 
    day -> int, day of the date 
    weekday -> int, [0,6] the weekday of the date 
    trans_cnt -> int, the transport cnt of the date 
    is_typhoon -> bool, is typhoon that date 
    is_working -> bool, whether the days need to work 
    day_type -> str, 'traditional', 'national', 'weekdend', 'weekday'
    is_foreign -> bool, is the date a foreign holiday 
    holi_type -> str, the type of the holiday 
    holi_lens -> int, the length of the not working day 
    phase -> str, 'start', 'mid', 'end'
    is_NYE -> bool, is new year eve 
    belong -> which holiday ( or weekend ) the day belong to
    '''

    ANOVA_df = pd.DataFrame( {
        'date': dates,
        'year': years,
        'month': months,
        'day': days,
        'weekday': weekdays,
        'trans_cnt': trans_cnts,
        'metro_cnt': mrt_cnts,
        'is_typhoon': is_typhoons,
        'is_working': is_workings,
        'day_type': day_types,
        'is_foreign': is_foreigns,
        'holi_type': holi_types,
        'holi_len': holi_lens,
        'phase': phase,
        'is_NYE': is_NYEs,
        'belong': belongs
    } )

    ANOVA_df.to_excel( 'ANOVA_df.xlsx' )


def build_dict( dates, values ):
    dates = list( dates )
    values = list( values )
    temp_dict = {}
    if len( dates ) != len( values ):
        raise Exception( 'Different Len' )

    for i in range( len( dates ) ):
        temp_dict[ dates[ i ] ] = values[ i ]

    return temp_dict


def friedman( df, drop=True ):
    df_rank = df.iloc[ :, 1: ].apply( grank, axis=1 )
    b, k = df_rank.shape
    T_all = df_rank.sum()
    print( T_all )
    Fr = ( ( 12 / ( b * k * ( k+1 ) ) ) * np.sum( T_all**2 ) ) - ( 3 * b * ( k+1 ) )
    pvalue = 1 - stats.chi2.cdf( Fr, k - 1 )
    return pvalue


def kruskal( *datas ):
    datas = list( datas )
    k = len( datas )
    for i in range( k ):
        datas[ i ] = np.array( datas[ i ] )

    alldatas = []
    for data in datas:
        for i in range( len( data ) ):
            alldatas.append( data[ i ] )
    alldatas.sort()

    temp_df = pd.DataFrame( { 'value': alldatas } )
    temp_df[ 'rank' ] = temp_df.index + 1

    v2r = temp_df.groupby( 'value' ).mean().reset_index()
    Tv = []
    ns = []

    for data in datas:
        ns.append( len( data ) )
        data_df = pd.DataFrame( { 'value': data } )
        Tv.append( pd.merge( data_df, v2r )[ "rank" ].sum() )

    Tv = np.array( Tv )
    ns = np.array( ns )
    n_sum = ns.sum()

    H = ( 12 / ( n_sum * ( n_sum+1 ) ) ) * ( sum( Tv**2 / ns ) ) - 3 * ( n_sum-1 )
    pvalue = 1 - stats.chi2.cdf( H, k - 1 )

    return pvalue


def Durbin_Watson_test( x ):
    x_square_sum = np.vdot( x, x )
    print( "x_square_sum = ", x_square_sum )
    size = x.size
    print( "size = ", size )
    x_d = np.zeros( ( size ) )
    print( "x_d = ", x_d )
    l_size = size - 1
    for i in range( l_size ):
        x_d[ i + 1 ] = x[ i + 1 ] - x[ i ]
    print( "x_d = ", x_d )
    d = np.vdot( x_d, x_d ) / x_square_sum
    print( "d = ", d )
    return ( d )


def runsTest( l, l_median ):
    runs, n1, n2 = 1, 0, 0
    if ( l[ 0 ] ) >= l_median:
        n1 += 1
    else:
        n2 += 1
    for i in range( 1, len( l ) ):
        if ( l[ i ] >= l_median and l[ i - 1 ] < l_median ) or ( l[ i ] < l_median and l[ i - 1 ] >= l_median ):
            runs += 1
        if ( l[ i ] ) >= l_median:
            n1 += 1
        else:
            n2 += 1
    runs_exp = ( ( 2*n1*n2 ) / ( n1+n2 ) ) + 1
    stan_dev = ( ( 2 * n1 * n2 * ( 2*n1*n2 - n1 - n2 ) ) / ( ( ( n1 + n2 )**2 ) * ( n1+n2-1 ) ) )**( 1 / 2 )
    z = ( runs-runs_exp ) / stan_dev
    pval_z = stats.norm.sf( abs( z ) ) * 2
    print( 'runs = ', runs )
    print( 'n1 = ', n1 )
    print( 'n2 = ', n2 )
    print( 'runs_exp = ', runs_exp )
    print( 'stan_dev = ', stan_dev )
    print( 'z = ', z )
    print( 'pval_z = ', pval_z )
    return pval_z