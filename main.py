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
import pickle
import model
import numpy as np
from noise import OrnsteinUhlenbeckProcess
from ctypes import windll
import datetime
import os

model = model.Actor()

#print("cuda available to torch: ", torch.cuda.is_available())

def navigate_to_lobby(driver):
    player_name = "PIayer" + str(random.randint(10, 99))

    username = driver.find_elements(by=By.ID, value="username")
    while not len(username) or not username[0].is_displayed():
        time.sleep(0.5)
        username = driver.find_elements(by=By.ID, value="username")
    username[0].send_keys(player_name) #change username
    driver.find_element(by=By.ID, value="skin-button").click()
    divs = driver.find_element(by=By.ID, value="color-list").find_elements(by=By.TAG_NAME, value="div")
    divs[-11].click() #get blue color
    driver.find_element(by=By.ID, value="skin-popup").find_element(by=By.CLASS_NAME, value="close-button").click()
    driver.find_element(by=By.ID, value="gamemode-4").click() #click button for 1v1 mode
    driver.find_element(by=By.ID, value="play-button").click() #click play

    close_tutorial = driver.find_element(by=By.ID, value="tuto-popup").find_element(by=By.CLASS_NAME, value="button")
    while (not close_tutorial.is_displayed()):
        time.sleep(0.5)
    close_tutorial.click()

    time.sleep(0.5)

    return player_name

while True:
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

    player_name = navigate_to_lobby(driver)

    while driver.current_url == "https://defly.io/":
        time.sleep(0.5)

    while not driver.current_url == "https://defly.io/#4-use4:3004":
        print("entered incorrect lobby, retrying, url:", driver.current_url)
        driver.quit()
        driver = webdriver.Chrome(options = opts)

        driver.get("https://defly.io/#4-use4:3004")
        driver.implicitly_wait(0)

        player_name = navigate_to_lobby(driver)

        while driver.current_url == "https://defly.io/":
            time.sleep(0.5)

    print("entered lobby")

    window_title_id = random.randint(0, 99999999)
    driver.execute_script(f'document.title = "{window_title_id:08}"')
    players = driver.find_elements(by=By.ID, value="gm1-player-")
    while (not len(players)):
        time.sleep(0.5)
        players = driver.find_elements(by=By.ID, value="gm1-player-")

    for i in range(len(players)):
        if (players[i].text[:8] != player_name and players[i].text[:6] == "PIayer"):
            players[i].click()
            challenge_text = driver.find_element(by=By.ID, value="gm-1v1-confirm-duel")
            button = challenge_text.find_element(by=By.CLASS_NAME, value="button")
            button.click()
            players = driver.find_elements(by=By.ID, value="gm1-player-")

    print("challenged available players")

    superpower = driver.find_element(by=By.ID, value="choose-superpower")
    chat_full = driver.find_element(by=By.ID, value="chat-history-full")
    chat = driver.find_element(by=By.ID, value="chat-history")
    challenge_accepted = False
    while(not superpower.is_displayed()):
        if challenge_accepted:
            break
        time.sleep(0.5)
        challenge_list = driver.find_element(by=By.ID, value="gm-1v1-duel-list");
        challenges = challenge_list.find_elements(by=By.CLASS_NAME, value="duel-text")
        buttons = challenge_list.find_elements(by=By.CLASS_NAME, value="button")
        for i in range(len(challenges)):
            try:
                if "PIayer" in challenges[i].text:
                    buttons[2 * i].click()
                    challenge_accepted = True
                    break
            except:
                continue

    print("in arena")

    now = datetime.datetime.now()
    id = f"{now.year:04}{now.month:02}{now.day:02}{now.hour:02}{now.minute:02}{now.second:02}"
    os.makedirs(f"data/{id}/images/large")
    os.makedirs(f"data/{id}/images/detail")
    os.makedirs(f"data/{id}/states")

    arrow_keys = [Keys.ARROW_UP, Keys.ARROW_DOWN, Keys.ARROW_LEFT, Keys.ARROW_RIGHT]
    move_dirx = 0
    move_diry = 0

    canvas_all = driver.find_elements(by=By.TAG_NAME, value="canvas")
    arena_canvas = canvas_all[-1]

    while(not superpower.is_displayed()):
        time.sleep(0.5)
    superpower.find_element(by=By.TAG_NAME, value="tbody").find_elements(by=By.TAG_NAME, value="tr")[1].find_elements(by=By.TAG_NAME, value="td")[3].click()
    #order of superpowers: dual fire, speed boost, clone, shield, flashbang, teleport

    shoot_only = True
    if shoot_only:
        ActionChains(driver).send_keys("11111111222222223333333344444444").perform() #get upgrades
    else:
        ActionChains(driver).send_keys("11111111222222224444444455555555").perform() #get upgrades

    #find window and prepare for screenshotting
    hwnd = None
    def find_chrome_handle(this_hwnd, unused):
        global hwnd
        if win32gui.IsWindowVisible(this_hwnd) and str(window_title_id) in win32gui.GetWindowText(this_hwnd):
            hwnd = this_hwnd
    win32gui.EnumWindows(find_chrome_handle, None)

    windll.user32.SetProcessDPIAware()

    result_block = driver.find_element(by=By.ID, value="gm-1v1-result")

    hsv_large_prev = None;
    hsv_detail_prev = None;
    hsv_large = None;
    hsv_detail = None;

    with open(f"data/{id}/log.txt", "a") as data_file:
        data_file.write("timestep screenshot process evaluate move save\n")

    is_training = True
    epsilon = 1.0
    ou_process = OrnsteinUhlenbeckProcess(size=4)
    i = 0
    while(arena_canvas.is_displayed() and not result_block.is_displayed()):
        start = time.time()
        img = vision.screenshot(hwnd)
        end = time.time()
        with open(f"data/{id}/log.txt", "a") as data_file:
            data_file.write(f"{i} {end - start} ")
        start = end
        img_nobar = vision.remove_bar(img)
        img_large = vision.crop_and_downsize(img_nobar, 1024, 1024, 8)
        img_detail = vision.crop_and_downsize(img_nobar, 256, 256, 2)
        hsv_large_prev = hsv_large
        hsv_detail_prev = hsv_detail
        hsv_large = vision.process(img_large)
        hsv_detail = vision.process(img_detail)
        if i == 0:
            hsv_large_prev = hsv_large
            hsv_detail_prev = hsv_detail
        data = torch.from_numpy(np.concatenate((hsv_large_prev, hsv_detail_prev, hsv_large, hsv_detail), axis=2))
        data = data.permute(2, 0, 1)
        data = data.float()
        data /= 256.0
        with open(f"data/{id}/states/{i}.pkl", "wb") as pickle_file:
            pickle.dump(data, pickle_file)
        data = data.unsqueeze(0)
        end = time.time()
        with open(f"data/{id}/log.txt", "a") as data_file:
            data_file.write(f"{end - start} ")
        start = end
        action = model(data).detach().numpy().squeeze(0)
        action += int(is_training) * epsilon * ou_process.sample()
        action = np.clip(action, -1., 1.)
        move_x = int(action[0] > 0) - int(action[1] > 0)
        move_y = int(action[2] > 0) - int(action[3] > 0)
        aim_x, aim_y = vision.aim(hsv_large)
        aim_x = max(-1.0, min(aim_x, 1.0))
        aim_y = max(-1.0, min(aim_y, 1.0))
        cursor_x = int(float(aim_x) * 100)
        cursor_y = int(float(aim_y) * 100)
        build = 0
        end = time.time()
        with open(f"data/{id}/log.txt", "a") as data_file:
            data_file.write(f"{end - start} ")
        start = end
        if (move_x == -1):
            ActionChains(driver, duration=0).key_down(Keys.ARROW_LEFT).key_up(Keys.ARROW_RIGHT).perform()
        if (move_x == 0):
            ActionChains(driver, duration=0).key_up(Keys.ARROW_LEFT).key_up(Keys.ARROW_RIGHT).perform()
        if (move_x == 1):
            ActionChains(driver, duration=0).key_up(Keys.ARROW_LEFT).key_down(Keys.ARROW_RIGHT).perform()
        if (move_y == -1):
            ActionChains(driver, duration=0).key_down(Keys.ARROW_UP).key_up(Keys.ARROW_DOWN).perform()
        if (move_y == 0):
            ActionChains(driver, duration=0).key_up(Keys.ARROW_UP).key_up(Keys.ARROW_DOWN).perform()
        if (move_y == 1):
            ActionChains(driver, duration=0).key_up(Keys.ARROW_UP).key_down(Keys.ARROW_DOWN).perform()
        if (shoot_only and not build):
            ActionChains(driver, duration=0).move_to_element_with_offset(arena_canvas, cursor_x, cursor_y).click_and_hold().perform() #distance right and down
        elif build:
            ActionChains(driver, duration=0).move_to_element_with_offset(arena_canvas, cursor_x, cursor_y).release().key_down(Keys.SPACE).key_up(Keys.SPACE).perform()
        elif i % 2 == 0:
            ActionChains(driver, duration=0).move_to_element_with_offset(arena_canvas, cursor_x, cursor_y).release().key_down(Keys.SPACE).key_up(Keys.SPACE).perform()
        else:
            ActionChains(driver, duration=0).move_to_element_with_offset(arena_canvas, cursor_x, cursor_y).key_up(Keys.SPACE).click_and_hold().perform()
        end = time.time()
        with open(f"data/{id}/log.txt", "a") as data_file:
            data_file.write(f"{end - start} ")
        start = end
        img_large = cv2.cvtColor(hsv_large, cv2.COLOR_HSV2BGR)
        img_detail = cv2.cvtColor(hsv_detail, cv2.COLOR_HSV2BGR)
        cv2.imwrite(f"data/{id}/images/large/{i}.png", img_large)
        cv2.imwrite(f"data/{id}/images/detail/{i}.png", img_detail)
        with open(f"data/{id}/actions.txt", "a") as data_file:
            data_file.write(' '.join(str(x) for x in action) + "\n")
        #cv2.imwrite(f"ss\{i}.png", img)
        end = time.time()
        with open(f"data/{id}/log.txt", "a") as data_file:
            data_file.write(f"{end - start}\n")
        i += 1
        if i >= 1200:
            break

    if i >= 1000:
        with open(f"data/{id}/result.txt", "a") as data_file:
            data_file.write("2\n")
    else:
        result_text = result_block.find_element(by=By.ID, value="gm-1v1-result-title").text
        if result_text[:8] == "You lost":
            with open(f"data/{id}/result.txt", "a") as data_file:
                data_file.write("0\n")
        elif result_text[:8] == "You defe":
            with open(f"data/{id}/result.txt", "a") as data_file:
                data_file.write("1\n")

    with open(f"data/{id}/length.txt", "a") as data_file:
        data_file.write(f"{i}\n")

    driver.quit()
