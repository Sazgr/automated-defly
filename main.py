from keys import Keys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import vision
import time
import torch
import random
import win32gui
import cv2
from ctypes import windll

#print("cuda available to torch: ", torch.cuda.is_available())

opts = Options()
#opts.add_argument('--headless')
opts.add_argument('--incognito')
opts.page_load_strategy = 'eager'
driver = webdriver.Chrome(options = opts)

#driver.get("https://defly.io")
driver.get("https://defly.io/#4-use4:3004")
#driver.get("https://defly.io/#4-eu1:3004")
#driver.set_window_size(800, 600)
driver.implicitly_wait(0)

username = driver.find_elements(by=By.ID, value="username")
while not len(username) or not username[0].is_displayed():
    time.sleep(0.5)
    username = driver.find_elements(by=By.ID, value="username")
username[0].send_keys("PIayer42") #change username
driver.find_element(by=By.ID, value="gamemode-4").click() #click button for 1v1 mode
driver.find_element(by=By.ID, value="play-button").click() #click play

close_tutorial = driver.find_element(by=By.ID, value="tuto-popup").find_element(by=By.CLASS_NAME, value="button")
while (not close_tutorial.is_displayed()):
    time.sleep(0.5)
close_tutorial.click()

time.sleep(0.5)

print("entered lobby")

players = driver.find_elements(by=By.ID, value="gm1-player-")
while (not len(players)):
    time.sleep(0.5)
    players = driver.find_elements(by=By.ID, value="gm1-player-")

for i in range(len(players)):
    if (False and players[i].text[:8] != "PIayer42" and players[i].text[:6] == "PIayer"):
        players[i].click()
        challenge_text = driver.find_element(by=By.ID, value="gm-1v1-confirm-duel")
        button = challenge_text.find_element(by=By.CLASS_NAME, value="button")
        button.click()
        players = driver.find_elements(by=By.ID, value="gm1-player-")

print("challenged available players")

superpower = driver.find_element(by=By.ID, value="choose-superpower")
chat_full = driver.find_element(by=By.ID, value="chat-history-full")
chat = driver.find_element(by=By.ID, value="chat-history")
while(not superpower.is_displayed()):
    time.sleep(0.5)
    challenge_list = driver.find_element(by=By.ID, value="gm-1v1-duel-list");
    challenges = challenge_list.find_elements(by=By.CLASS_NAME, value="duel-text")
    buttons = challenge_list.find_elements(by=By.CLASS_NAME, value="button")
    for i in range(len(challenges)):
        if "PIayer" in challenges[i].text:
            buttons[2 * i].click()
            break

print("in arena")

arrow_keys = [Keys.ARROW_UP, Keys.ARROW_DOWN, Keys.ARROW_LEFT, Keys.ARROW_RIGHT]
move_dirx = 0
move_diry = 0
while(chat_full.is_displayed()):
    time.sleep(0.5)

canvas_all = driver.find_elements(by=By.TAG_NAME, value="canvas")
arena_canvas = canvas_all[-1]

ActionChains(driver).send_keys("11111111222222223333333344444444").perform() #get upgrades

#find window and prepare for screenshotting
hwnd = None
def find_chrome_handle(this_hwnd, unused):
    global hwnd
    if win32gui.IsWindowVisible(this_hwnd) and 'Chrome' in win32gui.GetWindowText(this_hwnd):
            hwnd = this_hwnd
win32gui.EnumWindows(find_chrome_handle, None)

windll.user32.SetProcessDPIAware()

i = 0
while(not chat_full.is_displayed()):
    ActionChains(driver).key_up(Keys.ARROW_UP).key_up(Keys.ARROW_DOWN).key_up(Keys.ARROW_LEFT).key_up(Keys.ARROW_RIGHT).perform()
    move_dirx = random.randint(0, 2)
    move_diry = random.randint(0, 2)
    if (move_diry == 1):
        ActionChains(driver).key_down(Keys.ARROW_UP).perform()
    if (move_diry == 2):
        ActionChains(driver).key_down(Keys.ARROW_DOWN).perform()
    if (move_dirx == 1):
        ActionChains(driver).key_down(Keys.ARROW_LEFT).perform()
    if (move_dirx == 2):
        ActionChains(driver).key_down(Keys.ARROW_RIGHT).perform()
    ActionChains(driver).move_to_element_with_offset(arena_canvas, random.randint(-40, 40), random.randint(-40, 40)).perform() #distance right and down
    if (random.randint(0, 3) == 0):
        ActionChains(driver).key_down(Keys.SPACE).perform()
    else:
        ActionChains(driver).click_and_hold().perform()
    start = time.time()
    img = vision.screenshot(hwnd)
    cv2.imwrite(f"ss\{i}.png", img)
    end = time.time()
    print(end - start)
    i += 1

#process chat_full.text to determine whether 1v1 was won or lost

driver.quit()