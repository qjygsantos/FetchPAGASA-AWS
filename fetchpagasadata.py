from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from bs4 import BeautifulSoup
import pandas as pd
import datetime as dt
import calendar
import time

pagasa_link = 'http://121.58.193.173:8080/automatic/table.do'
msedgedriver_path = 'C:/path/to/msedgedriver.exe' 

headings = {'date': [], 'time': [], 'location': [], 'RF 10 Min [mm]': [], 'RF Daily Sum [mm]': [],
            'WD [deg]': [], 'WS [m/s]': [], 'Max WD [deg]': [], 'Max WS[m/s]': [], 'Temperature [℃]': [],
            'Humidity [%]': [], 'Pressure [hPa]': []}

def generateReportLog(date, location, dfInfo):
    with open("pagasaFetchLog", "a") as f:
        f.write(info)

def currentDateDisplayed(browser):
    formatDate = "%B/%d/%Y/%H:%M"
    tmp = browser.find_element(By.CLASS_NAME, 'dtpicker-value').text
    tmp = '/'.join([x.strip(',') for x in tmp.split()[1::]])
    return dt.datetime.strptime(tmp, formatDate)

def setDate(browser, startDate=dt.datetime(2011,10,29,00,00)):
    browser.find_element(By.CLASS_NAME, 'btn-icon').click()
    
    tmp = browser.find_element(By.CLASS_NAME, 'minutes')
    while currentDateDisplayed(browser).minute != 00:
        tmp.find_element(By.CLASS_NAME, "decrement").click()

    
    tmp = browser.find_element(By.CLASS_NAME, 'hour')
    while currentDateDisplayed(browser).hour != 00:
        tmp.find_element(By.CLASS_NAME, "decrement").click()

    tmp = browser.find_element(By.CLASS_NAME, 'year')
    while currentDateDisplayed(browser).year != startDate.year:
        if currentDateDisplayed(browser).year > startDate.year:
            tmp.find_element(By.CLASS_NAME, "decrement").click()
        else:
            tmp.find_element(By.CLASS_NAME, "increment").click()

    tmp = browser.find_element(By.CLASS_NAME, 'month')
    while currentDateDisplayed(browser).month != startDate.month:
        if currentDateDisplayed(browser).month > startDate.month:
            tmp.find_element(By.CLASS_NAME, "decrement").click()
        else:
            tmp.find_element(By.CLASS_NAME, "increment").click()

    tmp = browser.find_element(By.CLASS_NAME, 'day')
    while currentDateDisplayed(browser).day != startDate.day:
        if currentDateDisplayed(browser).day > startDate.day:
            tmp.find_element(By.CLASS_NAME, "decrement").click()
        else:
            tmp.find_element(By.CLASS_NAME, "increment").click()

    browser.find_element(By.CLASS_NAME, 'dtpicker-buttonSet').click()
    browser.find_element(By.CLASS_NAME, 'btn-search').click()
	
	
def incrementDay(browser):
    browser.find_element(By.CLASS_NAME, 'btn-icon').click()
    tmp = browser.find_element(By.CLASS_NAME, 'day')
    tmp.find_element(By.CLASS_NAME, "increment").click()
    browser.find_element(By.CLASS_NAME, 'dtpicker-buttonSet').click()
    browser.find_element(By.CLASS_NAME, 'btn-search').click()

def getDailyTable(browser, headings={'date': [], 'time': [], 'location': [], 'RF 10 Min [mm]': [], 'RF Daily Sum [mm]': [],
            'WD [deg]': [], 'WS [m/s]': [], 'Max WD [deg]': [], 'Max WS[m/s]': [], 'Temperature [℃]': [],
            'Humidity [%]': [], 'Pressure [hPa]': []}):
    time.sleep(2)
    topTable = browser.find_element(By.CLASS_NAME, "content-view-only").find_element(By.CLASS_NAME, "dataList")
    headings = {'date': [], 'time': [], 'location': [], 'RF 10 Min [mm]': [], 'RF Daily Sum [mm]': [],
            'WD [deg]': [], 'WS [m/s]': [], 'Max WD [deg]': [], 'Max WS[m/s]': [], 'Temperature [℃]': [],
            'Humidity [%]': [], 'Pressure [hPa]': []}
    locID = '11204301'
    output = pd.DataFrame(headings)
	
    
    topLocation = topTable.find_element(By.ID, locID).find_element(By.CLASS_NAME, 'first').text
    topTable.find_element(By.ID, locID).click()

    WebDriverWait(browser, timeout=15).until(ec.text_to_be_present_in_element((By.ID, "stationStr"), topLocation))

    bottomTable = browser.find_element(By.CLASS_NAME, "content-view-only").find_element(By.CLASS_NAME, 'view-head2')
    location = bottomTable.find_element(By.ID, 'stationStr').text
    date = browser.find_element(By.ID, 'searchtime').get_attribute("value").split()[0]

    print(date, location)
	

    botTable = browser.find_element(By.CLASS_NAME, "content-view-only").find_element(By.ID, 'detailTable')
    data = botTable.find_element(By.TAG_NAME, "tbody").get_attribute('innerHTML')
    soup = BeautifulSoup(data, features="html.parser")

    for row in soup.find_all('tr')[1::]:
        y = row.find_all('span')
        headings['date'].append(y[0].get_text().split()[0])
        headings['time'].append(y[0].get_text().split()[1])
        headings['location'].append(location)
        headings['RF 10 Min [mm]'].append(y[1].get_text())
        headings['RF Daily Sum [mm]'].append(y[2].get_text())
        headings['WD [deg]'].append(y[3].get_text())
        headings['WS [m/s]'].append(y[4].get_text())
        headings['Max WD [deg]'].append(y[5].get_text())
        headings['Max WS[m/s]'].append(y[6].get_text())
        headings['Temperature [℃]'].append(y[7].get_text())
        headings['Humidity [%]'].append(y[8].get_text())
        headings['Pressure [hPa]'].append(y[9].get_text())

    output = pd.concat([output, pd.DataFrame(headings)], ignore_index=True)
    return output

def goToMonth(browser, targetDate):
    setDate(browser, targetDate)

    numberOfDays = calendar.monthrange(targetDate.year, targetDate.month)[1]

    try:
        dataset = pd.DataFrame(headings)
        for i in range(numberOfDays):
            dataset = pd.concat([dataset, getDailyTable(browser)], ignore_index=True)
            incrementDay(browser)
    except Exception as e:
        print(e)
        dataset = pd.DataFrame(headings)
        for i in range(numberOfDays):
            dataset = pd.concat([dataset, getDailyTable(browser)], ignore_index=True)
            incrementDay(browser)

    tmp_df = dataset.drop_duplicates()
    tmp_df.to_csv(f"{targetDate.year}_{targetDate.month}_pagasa.csv")

if __name__ == "__main__":
    browser = webdriver.Edge(executable_path=msedgedriver_path)

    browser.get(pagasa_link)
    
    months = []
    month = dt.datetime(2022,1,1)
    
    for i in range(8):
        months.append(month)
        month = month + dt.timedelta(calendar.monthrange(month.year,month.month)[1])

    for month in months:
        try:
            goToMonth(browser, month)
        except Exception as e:
            goToMonth(browser, month)

    print("FINISH NA!")
