import os
import pickle
import cv2
import vision

def create_dataset():
    all_episodes = os.listdir("data")
    dataset = []
    for episode in all_episodes:
        with open(f"data/{episode}/length.txt", "r") as length_file:
            length = int(length_file.read())
        with open(f"data/{episode}/result.txt", "r") as result_file:
            result = int(result_file.read())

        if length < 40:
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
                reward += (1000 if result == 1 else -1000)

            if action[6] > 0:
                reward -= 30

            img = cv2.imread(f"data/{episode}/images/large/{i}.png")
            img = vision.crop_and_downsize(img, 100, 100, 1)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            for j in range(100):
                for k in range(100):
                    if img[j][k][1] >= 64 and img[j][k][2] >= 32 and img[j][k][0] == 0:
                        reward += 1

            data_point = {"state0" : state0_path, "action" : action, "reward" : reward, "state1" : state1_path, "terminal" : terminal}
            dataset.append(data_point)

        action_file.close()
        print(f"processed episode {episode}")

    with open(f"dataset.pkl", "wb") as pickle_file:
        pickle.dump(dataset, pickle_file)

def load_dataset():
    with open(f"dataset.pkl", "rb") as pickle_file:
        dataset = pickle.dump(pickle_file)

    return dataset

def create_batch(dataset, batch_size):
    state0_batch = []
    action_batch = []
    reward_batch = []
    state1_batch = []
    terminal_batch = []
    dataset_size = length(dataset)
    for i in range(batch_size):
        id = random.randint(0, dataset_size - 1)
        with open(dataset[id]["state0"], "rb") as pickle_file:
            state0 = pickle.load(pickle_file)
        state0_batch.append(state0)
        action_batch.append(dataset[id]["action"])
        reward_batch.append(dataset[id]["reward"])
        with open(dataset[id]["state1"], "rb") as pickle_file:
            state1 = pickle.load(pickle_file)
        state1_batch.append(state1)
        terminal_batch.append(0.0 if dataset[id]["terminal"] else 1.0)

        state0_batch = np.array(state0_batch).reshape(batch_size, -1)
        action_batch = np.array(action_batch).reshape(batch_size, -1)
        reward_batch = np.array(reward_batch).reshape(batch_size, -1)
        state1_batch = np.array(state1_batch).reshape(batch_size, -1)
        terminal_batch = np.array(terminal_batch).reshape(batch_size, -1)

        return state0_batch, action_batch, reward_batch, state1_batch, terminal_batch
