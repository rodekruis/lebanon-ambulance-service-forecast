import datetime
import azure.functions as func
from azure.storage.blob import BlobServiceClient, BlobClient
import logging
import os
import pandas as pd
import datetime
from prophet import Prophet


def download_input():
    """
    download and prepare input data
    """
    df_case_raw = pd.read_excel(r"data/lrc_missionExtensionBase.xlsx")
    df_case = df_case_raw.copy()

    # filter based on dates (optional)
    df_case = df_case[df_case.lrc_ArrivalatDestination.dt.year >= 2019]
    df_case = df_case[df_case.lrc_ArrivalatDestination <= pd.to_datetime(datetime.date(year=2020, month=9, day=1))]
    # aggregate by date: count number of cases per day
    df_case = df_case.groupby(pd.Grouper(key='lrc_ArrivalatDestination', freq='D'))[
        'lrc_missionId'].size().reset_index().sort_values('lrc_ArrivalatDestination')
    # prepare dataframe for facebook prophet
    df_case = df_case.rename(columns={'lrc_ArrivalatDestination': 'ds', 'lrc_missionId': 'y'})
    # keep only last year (optional)
    df_case = df_case[-365:]

    return df_case


def upload_output(df_output):
    """
    upload output data, TBI
    """


def forecast(df_input, forecast_window=90):
    """
    forecast number of cases in the future
    Keyword arguments:
    forecast_window -- number of days to forecast in the future (default 90)
    """
    # fit model
    m = Prophet(yearly_seasonality=True)
    m.fit(df_input)
    # predict
    future = m.make_future_dataframe(periods=forecast_window)
    df_output = m.predict(future)
    return df_output


def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due')
    try:
        df_input = download_input()
        df_output = forecast(df_input)
        upload_output(df_output)
    except Exception as e:
        logging.error('Error:')
        logging.error(e)

    logging.info('Python timer trigger function ran at %s', utc_timestamp)
