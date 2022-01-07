import datetime
import logging
import azure.functions as func
from selenium import webdriver
from azure.identity import DefaultAzureCredential, ClientSecretCredential
import datetime 
import os
import psycopg2
from psycopg2.extras import execute_values
import pandas as pd


def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)

    host = "serverxx.postgres.database.azure.com port = 5432"
    dbname = "django_server"
    user = "serverxx"
    password = "google@99"
    sslmode = "require"
    conn_string = "host={0} user={1} dbname={2} password={3} sslmode={4}".format(host, user, dbname, password, sslmode)

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome("/usr/local/bin/chromedriver", chrome_options=chrome_options)
    driver.get('https://www.bangaloreairport.com/kempegowda-departures')
    items = driver.find_elements_by_xpath('.//div[@class = "flight-row"]')
    data = []
    for item in items:
        try:
            k = {}
            k['departure'] = item.find_element_by_xpath('.//div[1]').text
            k['time'] = item.find_element_by_xpath('.//div[2]//div[1]').text
            k['flight'] = item.find_element_by_xpath('.//div[2]//div[2]').text
            k['airline'] = item.find_element_by_xpath('.//div[2]//div[3]').text
            k['info_url'] = item.find_element_by_xpath('.//div[2]').find_element_by_tag_name('a').get_attribute('href')
            k['status'] = item.find_element_by_xpath('.//div[contains(@class ,"flight-col flight-col__status")]').text
            data.append(k)
        except:
            pass
    df_departure = pd.DataFrame(data)
    df_departure['is_departure'] = True
    ####----------------------------------###############
    driver.get('https://www.bangaloreairport.com/kempegowda-arrivals')
    items = driver.find_elements_by_xpath('.//div[@class = "flight-row"]')
    data = []
    for item in items:
        try:
            k = {}
            k['departure'] = item.find_element_by_xpath('.//div[1]').text
            k['time'] = item.find_element_by_xpath('.//div[2]//div[1]').text
            k['flight'] = item.find_element_by_xpath('.//div[2]//div[2]').text
            k['airline'] = item.find_element_by_xpath('.//div[2]//div[3]').text
            k['info_url'] = item.find_element_by_xpath('.//div[2]').find_element_by_tag_name('a').get_attribute('href')
            k['status'] = item.find_element_by_xpath('.//div[contains(@class ,"flight-col flight-col__status")]').text
            data.append(k)
        except:
            pass
 
    df_arrival = pd.DataFrame(data)
    df_arrival['is_departure'] = False
    df = pd.concat([df_arrival,df_departure],axis = 0).reset_index(drop=True)
    df = df.sort_values('time')
    try:
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM fly_flightboard ")
        conn.commit()
        cursor.close()
        conn.close()
    except :
        pass
    data = [df.T.to_dict()[i] for i in range(len(df))]
    columns = data[0].keys()
    query = "INSERT INTO fly_flightboard ({}) VALUES %s".format(','.join(columns))
    values = [[value for value in project.values()] for project in data]
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    logging.info('connection_done')
    execute_values(cursor, query, values)
    conn.commit()
    cursor.close()
    conn.close()
