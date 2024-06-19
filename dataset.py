import os
import pickle
import cv2
import vision
import random
import numpy as np

def create_dataset():
    all_episodes = os.listdir("data")

    try:
        with open(f"dataset.pkl", "rb") as pickle_file:
            dataset = pickle.load(pickle_file)
    except:
        print("previous dataset not found, creating new dataset")
        dataset = {"data" : [], "info_latest" : "00000000000000", "size" : 0}

    for episode in all_episodes:
        if episode <= dataset["info_latest"]:
            print(f"skipped episode {episode}")
            continue

        with open(f"data/{episode}/length.txt", "r") as length_file:
            length = int(length_file.read())
        with open(f"data/{episode}/result.txt", "r") as result_file:
            result = int(result_file.read())

        if length < 45:
            continue

        action_file = open(f"data/{episode}/actions.txt")
        for i in range(30):
            action_file.readline()

        for i in range(30, length - 12):
            state0_path = f"data/{episode}/states/{i}.pkl"
            action = [float(x) for x in action_file.readline().split()]
            state1_path = f"data/{episode}/states/{i + 1}.pkl"
            terminal = (i == length - 13)

            reward = 0

            if terminal:
                reward += (2000 if result == 1 else -2000 if result == 0 else -200)

            if (action[6] > 0):
                reward -= 10 #penalize agent for not shooting

            img = cv2.imread(f"data/{episode}/images/large/{i}.png")
            img = vision.crop_and_downsize(img, 100, 100, 1)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

            own_pixels = 0
            enemy_pixels = 0
            out_of_bound_pixels = 0

            for j in range(100):
                for k in range(100):
                    if img[j][k][1] >= 64 and img[j][k][2] >= 32 and img[j][k][0] == 0:
                        enemy_pixels += 0.01 * ((50 - abs(j - 50)) + (50 - abs(k - 50)))
                    if img[j][k][1] >= 64 and img[j][k][2] >= 32 and (img[j][k][0] > 110 and img[j][k][0] < 120):
                        own_pixels += 1
                    if img[j][k][1] < 10 and img[j][k][2] < 80:
                        out_of_bound_pixels += 0.01 * ((50 - abs(j - 50)) + (50 - abs(k - 50)))

            reward += 4 * min(enemy_pixels, 40) #reward agent for being near enemy
            reward -= 0.25 * max(own_pixels - 50, 0) #penalize agent for building too many walls
            reward -= 0.1 * out_of_bound_pixels #penalize the agent for being too close to arena wall

            #print(reward) #for inspecting and debugging

            data_point = {"state0" : state0_path, "action" : action, "reward" : reward, "state1" : state1_path, "terminal" : terminal}
            dataset["data"].append(data_point)
            dataset["size"] += 1

        action_file.close()
        if (episode > dataset["info_latest"]):
            dataset["info_latest"] = episode
        print(f"processed episode {episode}, dataset size is {dataset['size']}")

    with open(f"dataset.pkl", "wb") as pickle_file:
        pickle.dump(dataset, pickle_file)

def load_dataset():
    with open(f"dataset.pkl", "rb") as pickle_file:
        dataset = pickle.load(pickle_file)

    return dataset["data"]

def create_batch(dataset, batch_size):
    state0_batch = []
    action_batch = []
    reward_batch = []
    state1_batch = []
    terminal_batch = []
    dataset_size = len(dataset)
    for i in range(batch_size):
        augment_flip = random.randint(0, 1)
        id = random.randint(0, dataset_size - 1)
        with open(dataset[id]["state0"], "rb") as pickle_file:
            state0 = pickle.load(pickle_file).numpy().reshape(12, 128, 128)
            if augment_flip:
                np.flip(state0, axis=2)
        state0_batch.append(state0)
        action = np.array(dataset[id]["action"])
        if augment_flip:
            action[0], action[1] = action[1], action[0]
            action[2], action[3] = action[3], action[2]
            action[4] = -action[4]
        action_batch.append(action)
        reward_batch.append(dataset[id]["reward"])
        with open(dataset[id]["state1"], "rb") as pickle_file:
            state1 = pickle.load(pickle_file).numpy().reshape(12, 128, 128)
            if augment_flip:
                np.flip(state1, axis=2)
        state1_batch.append(state1)
        terminal_batch.append(0.0 if dataset[id]["terminal"] else 1.0)
    state0_batch = np.array(state0_batch).reshape(batch_size, 12, 128, 128)
    action_batch = np.array(action_batch).reshape(batch_size, -1)
    reward_batch = np.array(reward_batch).reshape(batch_size, -1)
    state1_batch = np.array(state1_batch).reshape(batch_size, 12, 128, 128)
    terminal_batch = np.array(terminal_batch).reshape(batch_size, -1)

    return state0_batch, action_batch, reward_batch, state1_batch, terminal_batch
