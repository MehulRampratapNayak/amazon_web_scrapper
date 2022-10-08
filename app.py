from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen as uReq
from selenium import webdriver
import csv
import pandas as pd

app = Flask(__name__)

@app.route('/',methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")


def extract_record(item):
    #description&url
    atag=item.h2.a
    description=atag.text.strip()
    url="https://www.amazon.in"+atag.get('href')
    
    try:
        
        #price
        price_parent=item.find('span','a-price')
        price=price_parent.find('span','a-price-whole').text.strip()
    except AttributeError:
        return
    try:    
        #rank and rating
        rating=item.i.text
        review_count=item.find('span',{'class':'a-size-base'}).text
    except AttributeError:
        rating=''
        review_count=''
    
    result=(description,price,rating,review_count,url)
    
    return result

def get_url(search_term):
    """ Generate a URL for the search term"""
   # template="https://www.amazon.ae/s?k=salama+care&crid=2WHGND4NAFUT3&sprefix=salama+care%2Caps%2C176&ref=nb_sb_noss_1
    template="https://www.amazon.in/s?k={}&crid=3JKZD4EXHPZC&sprefix=%2Caps%2C432&ref=nb_sb_ss_recent_1_0_recent"
    search_term=search_term.replace(' ','+')
    
    #add term query to url
    url=template.format(search_term)
    
    #add page query place holder
    url += '&page{}'
    
    return url

@app.route('/scrapper',methods=['POST','GET']) # route to show the review comments in a web UI
@cross_origin()
def search_query():
    if request.method == 'POST':
        try:
            search_term = request.form['content'].title().replace(" ","")
            driver=webdriver.Chrome("C:\\Mehul\Data Scientist\\Amazon Scrapper\\amazon_scraper\\chrome_driver\\chromedriver_win32\\chromedriver.exe")
            
            records=[]
            url=get_url(search_term)
    
            for page in range(1,21):

                driver.get(url.format(page))
                soup=BeautifulSoup(driver.page_source,'html.parser')
                results=soup.find_all('div',{'data-component-type':'s-search-result'})
        
                for item in results:
                    record=extract_record(item)
                    if record: 
                        records.append(extract_record(item))
                        #print(records)
                
            driver.close()   
    
    #save the data to csv file
            filename = search_term + ".csv"
            with open(filename,"w",newline='',encoding='utf-8') as f:
                writer=csv.writer(f)
                writer.writerow(['Description','Price(Rs)','Rating','Review Count','Url of the Product'])
                writer.writerows(records) 
                
    #converting the  csv file to dictionary for inserting it into the table
            input_file = csv.DictReader(open(filename,encoding='utf-8'))
            scrapper=[i for i in input_file]    
            return render_template('results.html', scrapper=scrapper[0:(len(scrapper)-1)])    
        except Exception as e:
            print('The Exception message is: ',e)
            return 'something is wrong'
    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8001, debug=True)
	#app.run(debug=True)
