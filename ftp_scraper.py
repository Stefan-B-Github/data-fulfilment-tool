from selenium import webdriver
import os
import platform
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
import email_sender

#This uses a scraper to navigate web FTPs
class ftp_scraper:
    def get_driver():
        chrome_options = Options()
        if (platform.system() == 'Windows'):
            driver = webdriver.Chrome('C:/users/Stefan/Downloads/chromedriver', options=chrome_options)
        else:
            chrome_options.headless = True
            chrome_options.binary_location = "/usr/bin/chromium"
            chrome_options.add_argument("--disable-dev-shm-using") 
            chrome_options.add_argument("--disable-extensions") 
            chrome_options.add_argument("--disable-gpu") 
            chrome_options.add_argument("--user-data-dir=/home/testuser") 
            chrome_options.add_argument("--disable-software-rasterizer") 
            chrome_options.add_argument("--no-sandbox") 
            driver = webdriver.Chrome('/bin/chromedriver', options=chrome_options)
        return driver

    def sendfile(filePath, fileName, type):
        if (platform.system() != 'Windows'):
            filePath = "/" + filePath
        driver = ftp_scraper.get_driver()
        if type == 'DSB':
            n = 0
            error = "none"
            while n < 10:
                try:
                    return ftp_scraper.send_to_dsb(filePath, fileName, driver)
                except Exception as e:
                    error = str(e)
                    print("Error with DSB: " + error + ". " + str(10-n) + " attempts left.")
                    driver.quit()
                    driver = ftp_scraper.get_driver()
                    n += 1
            email_sender.send_error_message("DSB FTP prepration", fileName, error)
            driver.quit()
            return False
        elif type == "Amaze":
            return ftp_scraper.send_to_amaze(filePath, fileName, driver)
        return False

    def send_to_amaze(filePath, fileName, driver):
        url = "https://example.co.uk/Login"
        status = True
        driver.get(url)
        driver.find_element_by_name('RumpusLoginUserName').send_keys("USER")
        driver.find_element_by_name('RumpusLoginPassword').send_keys("PASS")
        driver.find_element_by_id('loginButton').click() #log in
        status = ftp_scraper.wait_for_element(driver, "AM_Menu", By.ID)
        driver.execute_script('OpenDrop()') #Load file dialog
        uploadID = 'FileSelectInput'
        status = ftp_scraper.wait_for_element(driver, uploadID, By.ID)
        ftp_scraper.wait(driver, 2)
        driver.find_element_by_id(uploadID).send_keys(filePath + "/" + fileName) #Upload file
        ftp_scraper.wait(driver, 2)
        driver.find_element_by_id('BeginUploadSubmit').click() #Send file
        ftp_scraper.wait(driver, 2)
        driver.quit()
        print("done!")
        return status

    def send_to_dsb(filePath, fileName, driver): #DSB
        url = "https://example.net/WebInterface/login.html"
        driver.get(url)
        status = True
        driver.find_element_by_name('username').send_keys("Aditus")
        driver.find_element_by_name('password').send_keys("right-893+mother")
        driver.find_element_by_id('btnLogin').click() #log in
        xpath_to_dsb_button =  "/html/body/div[3]/div/div[5]/div[16]/div/div[3]/div[1]/table/tbody/tr/td[2]/a" 
        status = ftp_scraper.wait_for_element(driver, xpath_to_dsb_button, By.XPATH)
        driver.find_element_by_xpath(xpath_to_dsb_button).click() #Go to "to DSB" option
        upload_name = "file_1_SINGLE_FILE_POST"
        status = ftp_scraper.wait_for_element(driver, upload_name, By.NAME)
        driver.execute_script('performAction("Upload")') #Load file dialog
        ftp_scraper.wait(driver, 2)
        driver.find_element_by_name(upload_name).send_keys(filePath + "/" + fileName) #Upload file
        ftp_scraper.wait(driver, 2)
        driver.quit()
        print("done!")
        return status

    def wait_for_element(driver, elementName, type):
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((type, elementName)))
            print("Page is ready!")
            return True
        except TimeoutException:
            print("Loading took too much time!")
            return False


    def wait(driver, time):
        try:
            WebDriverWait(driver, time).until(EC.presence_of_element_located((By.NAME, "not_here"))) #Adds an arbitrary wait.
        except TimeoutException:
            print("waited")
            True
