from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.proxy import Proxy, ProxyType
import time
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
import random
from rq import get_current_job
import redis
from create_db import db



#selectors:
AGE_VERIF_BUTTON = '/html/body/div[1]/div/div[2]/div[2]/div/div/div[1]/div/div/div[2]/button' #xpath
MAIN_LOGIN_BUTTON = '#login-button' #ID
USER_NAME_AREA = '//*[@id="login-username"]' #ID
USER_PASS_AREA = '//*[@id="login-password"]' #ID
LOGIN_BUTTON = '/shreddit-async-loader/auth-flow-login/faceplate-form/faceplate-tabpanel/auth-flow-modal[1]/div[1]/div[3]' #XPATH
UPVOTE_BUTTON = ["/html/body/div[1]/div/div[2]/div[2]/div/div[1]/div/div[2]/div[3]/div[1]/div[3]/div[1]/div/div[1]/div/button[1]", #"//*[starts-with(@id, 'upvote-button')]"
                 "/html/body/div[1]/div/div[2]/div[3]/div/div/div/div[2]/div[1]/div[3]/div[1]/div/div[1]/div/button[1]",
                 "/html/body/div[1]/div/div[2]/div[2]/div/div/div/div[2]/div[2]/div[1]/div[3]/div[1]/div/div[1]/div/button[1]"

                ]






class RedditBot:
    def __init__(self, username, password, link):
        ua = UserAgent()
        proxy_server = "51.91.197.157"
        proxy_port = 3003
        user_agent = ua.random
        chrome_options = Options()
        chrome_options.add_argument(f'--proxy-server={proxy_server}:{proxy_port}')
        chrome_options.add_argument("--lang=en")
        chrome_options.add_argument("--blink-settings=imagesEnabled=false")
        #chrome_options.add_argument("--headless")
        chrome_options.add_argument("user-agent=" + user_agent)
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--start-maximized")
        ChromeDriverManager().install()


        
        self.link = link
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        
        self.sleep_timer = random.randint(100, 999) / 1000
        sleep(2)
        self.log_in(username, password)


    def quit_driver(self):
        print('quit')
        self.driver.quit()



    def save_result(self, result):
        redis_conn = redis.Redis(host='localhost', port=6379)
        current_job = get_current_job(redis_conn)
        job_id = current_job.get_id()
        db.db_save_job_result(job_id, result)

    


    def log_in(self, username, password):
        self.driver.get("https://2ip.ua")
        #time.sleep(10)
        self.driver.get("https://www.reddit.com/")
        time.sleep(3)
        res = ' '
        try:
            try:
                self.driver.switch_to.frame(self.driver.find_elements(By.CSS_SELECTOR, "#credential_picker_container iframe")[0])
                self.driver.find_element(By.XPATH, '/html/body/div/div[1]/div/div[1]/div[2]').click()
                sleep(self.sleep_timer)
                self.driver.find_element(By.XPATH, '/html/body/div/div[1]/div/div[1]/div[2]').send_keys(Keys.ESCAPE)
            except Exception as e:
                res = 'picker'
                print('picker')
                pass
            finally:
                sleep(self.sleep_timer)
                self.driver.find_element(By.CSS_SELECTOR, 'body').send_keys(Keys.ESCAPE)
                sleep(self.sleep_timer)
                self.driver.find_element(By.CSS_SELECTOR, MAIN_LOGIN_BUTTON).click()
                self.wait.until(EC.invisibility_of_element_located((By.XPATH, USER_NAME_AREA)))
                time.sleep(4)
                self.driver.find_element(By.XPATH, USER_NAME_AREA).send_keys(username)
                time.sleep(self.sleep_timer)
                self.driver.find_element(By.XPATH, USER_PASS_AREA).send_keys(password)
                time.sleep(self.sleep_timer)
                self.driver.find_element(By.XPATH, USER_PASS_AREA).send_keys(Keys.ENTER)
                self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "#USER_DROPDOWN_ID"))) # logged into acc
        except Exception as e:
            self.quit_driver()
            try:
                result = res + f'no login in acc + {e}'
                with open('check_log_pass.txt', 'a') as f:
                    text = f'{username}:{password} - {str(e)[:300]}\n'
                    f.write(text)
                self.save_result(result)
                return
            except Exception:
                return
        self.get_post_and_upvote()
        

    def get_post_and_upvote(self):
        sleep(4)
        self.driver.get(self.link)
        sleep(1)
        try:
            self.wait.until(EC.presence_of_element_located((By.XPATH, AGE_VERIF_BUTTON))).click()
            sleep(5)
        except Exception:
            pass
        finally:
            self.driver.find_element(By.CSS_SELECTOR, 'body').send_keys(Keys.ESCAPE)
            self.driver.switch_to.active_element.send_keys(Keys.ESCAPE)
            try:
                up_button = self.driver.find_element(By.CSS_SELECTOR, '._2rszc84L136gWQrkwH6IaM > div:nth-child(1) > div:nth-child(1) > div > button:nth-child(1)')
                aria_pressd = up_button.get_attribute('aria-pressed')
                if aria_pressd == "false":
                    up_button.click()
                    result = 'upvote_ok'
                    self.save_result(result)
                else:
                    result = 'upvote_ok'
                    self.save_result(result)
            except NoSuchElementException:
                try:
                    for botton in UPVOTE_BUTTON:
                        upv_but = self.driver.find_element(By.XPATH, botton)
                        aria_pressed = upv_but.get_attribute('aria-pressed')
                        if aria_pressed == "false":
                            upv_but.click()
                            result = 'upvote_ok'
                            self.save_result(result)
                        else:
                            result = 'upvote_ok'
                            self.save_result(result)
                except NoSuchElementException:
                    pass
            self.quit_driver()



def gomain(args):
    RedditBot(args[0], args[1], args[2])
    
#q = RedditBot(username, password, link)

#gomain(args)


