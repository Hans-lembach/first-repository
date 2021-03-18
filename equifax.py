from os import rename, path
import time
import pandas as pd
import numpy as np

import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from python3_anticaptcha.NoCaptchaTaskProxyless import NoCaptchaTaskProxyless



download_dir = "/home/andres/LEMONPOT_PRACTICA_HANS/VentiPay/pdf_equifax_2"



def esperarElemento(driver, elemento, xpath = True, timeout = 100, after = 0):
    method = By.XPATH if xpath else By.ID
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located(
            (method, elemento)
        )
    )
    time.sleep( after )


def open_driver(headless = True):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.headless = True if headless else False
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument('log-level=3')
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    prefs = {'download.default_directory' : download_dir}
    chrome_options.add_experimental_option('prefs', prefs)
    driver = webdriver.Chrome("/home/andres/LEMONPOT_PRACTICA_HANS/VentiPay/chromedriver", options=chrome_options)
    return driver


def enviar(driver, input_id, value):
    input_element = driver.find_element_by_id(input_id)
    input_element.click()
    input_element.send_keys(value)


def login(driver):
    ANTICAPTCHA_KEY = "981fdde1371951da646e2e3e01682a3e"
    WEB_URL = "https://sec.equifax.cl/"
    SITE_KEY = "6LcyIf8UAAAAAI579dqqx5yLZW0I8qoLofHLZvAr"

    driver.get("https://sec.equifax.cl/clients/home")
    enviar(driver, "username", "CRISTIANMELENDE.ADMI")
    enviar(driver, "password", "pazbap-zybmE4")
    print("TRYING RECAPTCHA")
    captcha_obj = NoCaptchaTaskProxyless(anticaptcha_key = ANTICAPTCHA_KEY)
    captcha_result = captcha_obj.captcha_handler(websiteURL = WEB_URL, websiteKey = SITE_KEY)
    solucion = captcha_result["solution"]["gRecaptchaResponse"]
    driver.execute_script(
            "document.getElementById('g-recaptcha-response').style.display = 'block';"
        )
    recaptcha_element = driver.find_element_by_xpath('//*[@id="g-recaptcha-response"]')
    recaptcha_element.send_keys(solucion)

    driver.find_element_by_name("loginForm").submit()
    esperarElemento(driver, "destacados", False)
    print("LOGGED IN")


def scraper(driver, rut):
    driver.get("https://sec.equifax.cl/clients/products?2576e4=7c9fa136d4413fa6173637e883b6998d32e1d675f88cddff9dcbcf331820f4b8&9e27eb=7c9fa136d4413fa6173637e883b6998d32e1d675f88cddff9dcbcf331820f4b8")

    esperarElemento(driver, "sendForm", False)
    driver.find_element_by_id("0c27700c82d333aa295692f1814040a962d7bc530253af661d97635dd5ed7af9").click()
    esperarElemento(driver, "rut", False)
    enviar(driver, "rut", rut)
    driver.find_element_by_id("btnChkSbmt").click()
    esperarElemento(driver, "top", False, 150)
    pdf = driver.find_element_by_xpath("//div[contains(@class, 'herramientas')]/div[2]/div/a[1]").get_attribute("href")
    #DESCARGA EL PDF
    driver.get(pdf)
    exists = path.exists(f"{download_dir}/platinum.pdf")
    while not exists:
        time.sleep(1)
        exists = path.exists(f"{download_dir}/platinum.pdf")
    rename(f"{download_dir}/platinum.pdf", f"{download_dir}/{rut}.pdf")


driver = open_driver()
login(driver)



lista_rut = list(pd.read_csv('ruts_por_scrap_equifax.csv', index_col=0)['ruts'])

for rut in lista_rut:
    try:
        scraper(driver, rut)
        print(f"{rut} CORRECTO")
    except Exception as e:
        print(f"{rut} FALLIDO")
        print(e)
