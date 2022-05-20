import pandas as pd
import datetime as dt


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