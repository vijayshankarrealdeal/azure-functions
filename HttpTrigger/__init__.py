import logging
import time
import json
import azure.functions as func
from selenium import webdriver
from selenium.webdriver.common.by import By
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from datetime import datetime
import os

def main(req: func.HttpRequest) -> func.HttpResponse:

    request_body = req.get_json()

    if request_body.get('hotel') == True:
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument(f'user-agent={user_agent}')
        driver = webdriver.Chrome("/usr/local/bin/chromedriver", chrome_options=chrome_options)
        driver.maximize_window()
        check_n = request_body.get('checkin').split('-')
        check_in = check_n[1]+check_n[-1]+check_n[0]
        check_o = request_body.get('checkout').split('-')
        check_out = check_o[1]+check_o[-1]+check_o[0]
        url = f'https://www.makemytrip.com/hotels/hotel-listing/?checkin={check_in}&checkout={check_out}&locusId=CTBLR&locusType=city&city=CTBLR&country=IN&searchText=Kempegowda%20Airport%2C%20Bangalore&roomStayQualifier=1e0e&_uCurrency=INR&mmPoiTag=POI%7CKempegowda%20Airport%7CPOI53346%7C13.20449%7C77.70769&reference=hotel&type=city'
        driver.get(url)
        for i in range(1,10):
            driver.execute_script(f'window.scrollTo(0, {1080*i})') 
            time.sleep(2)
        cards = driver.find_elements(By.XPATH,'.//div[contains(@id,"Listing_hotel_")]')
        data = []
        for card in cards:
            try:
                data.append(
                {
                "img" : card.find_element(By.CLASS_NAME,'imgCont').find_element(By.TAG_NAME,'img').get_attribute('src'),
                "hotel_name" : card.find_element(By.XPATH,'.//p[@id = "hlistpg_hotel_name"]').text,
                "rating" : card.find_element(By.XPATH,'.//span[@id = "hlistpg_hotel_user_rating"]').text,
                "distance" : card.find_element(By.CLASS_NAME,'pc__html').text,
                "price" : card.find_element(By.XPATH,'.//p[@id = "hlistpg_hotel_shown_price"]').text,
                "tax" : card.find_element(By.XPATH,'.//p[contains(@class,"font12 darkGrey")]').text
                })
            except:
                pass
    else:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome("/usr/local/bin/chromedriver", chrome_options=chrome_options)
        driver.maximize_window()
        origin_code = request_body.get('origin_code')
        orginName = request_body.get('orginName')
        destination_code = request_body.get('destination_code')
        destinaitionName = request_body.get('destinaitionName')
        departure_date = request_body.get('departure_date')
        adult = request_body.get('adult')
        child = request_body.get('child')
        infant = request_body.get('infant')
        url = f'https://www.air.irctc.co.in/onewaytrip?type=O&origin={origin_code}&originCity={orginName}&originCountry=IN&destination={destination_code}&destinationCity={destinaitionName}&destinationCountry=IN&flight_depart_date={departure_date}&ADT={adult}&CHD={child}&INF={infant}&class=Economy&airlines=&ltc=0&searchtype=&isDefence=0&bookingCategory=0'
        driver.get(url)
        time.sleep(5)
        details = driver.find_elements(By.CLASS_NAME,'right-searchbarbtm')
        data = []
        for detail in details[:15]:
            sub_div = detail.find_element(By.CLASS_NAME,'right-searchbarbtm-in')
            fight_name_no =  sub_div.find_element(By.XPATH,'./div[1]').text.split('\n')
            orgin_time_palce = sub_div.find_element(By.XPATH,'./div[2]').text.split('\n')
            destinaiton_time_place = sub_div.find_element(By.XPATH,'./div[3]').text.split('\n')
            time_stop = sub_div.find_element(By.XPATH,'./div[4]').text.split('\n')
            price_refund = sub_div.find_element(By.XPATH,'./div[5]').text.split('\n')
            data.append({
            "flight_image" : sub_div.find_element(By.TAG_NAME,'img').get_attribute('src'),
            "fight_name" : fight_name_no[0],
            "flight_no":fight_name_no[1],
            "origin_time" : orgin_time_palce[0],
            "origin_place":orgin_time_palce[1],
            "destination_time" : destinaiton_time_place[0],
            "destination_place":destinaiton_time_place[1],
            "duration_stop" : time_stop[0],
            "no_stops":time_stop[1],
            "price" : price_refund[0],
            "refund":price_refund[1]
            })

    driver.close()
    return func.HttpResponse(
             json.dumps({"data":data}),
             status_code=200
    )