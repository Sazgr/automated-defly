import dataset
import ddpg

def train(num_iterations, agent, output):
    step = 0
    while step < num_iterations:
        agent.update_policy()
        step += 1
        if step % 1 == 0:
            print(f"step {step} reached")
            agent.save_model(output, step)


do_training = True

if __name__ == "__main__":
    if do_training:
        dataset.create_dataset()
        ddpg = ddpg.DDPG()
        train(10000, ddpg, "nets")
    else:
        pass