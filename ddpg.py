import torch
import torch.nn as nn
import dataset
import numpy as np
from model import (Actor, Critic)
from torch.optim import Adam

def soft_update(target, source, tau):
    for target_param, param in zip(target.parameters(), source.parameters()):
        target_param.data.copy_(
            target_param.data * (1.0 - tau) + param.data * tau
        )

def hard_update(target, source):
    for target_param, param in zip(target.parameters(), source.parameters()):
            target_param.data.copy_(param.data)

class DDPG(object):
    def __init__(self):
        self.dataset = dataset.load_dataset()
        self.actor = Actor()
        self.actor_target = Actor()
        self.actor_optim  = Adam(self.actor.parameters(), lr=0.0001)

        self.critic = Critic()
        self.critic_target = Critic()
        self.critic_optim  = Adam(self.critic.parameters(), lr=0.001)

        hard_update(self.actor_target, self.actor)
        hard_update(self.critic_target, self.critic)

        self.loss = nn.MSELoss()

        # Hyper-parameters
        self.batch_size = 64
        self.tau = 0.001
        self.discount = 0.97

    def update_policy(self):
        state0_batch, action_batch, reward_batch, state1_batch, terminal_batch = dataset.create_batch(self.dataset, self.batch_size)

        next_q_values = self.critic_target([
            torch.from_numpy(state1_batch),
            self.actor_target(torch.from_numpy(state1_batch)),
        ])

        torch.no_grad(next_q_values)

        target_q_batch = torch.from_numpy(reward_batch).float() + self.discount * torch.from_numpy(terminal_batch).float() * next_q_values

        self.critic.zero_grad()

        q_batch = self.critic([torch.from_numpy(state0_batch), torch.from_numpy(action_batch).float()])

        value_loss = self.loss(q_batch, target_q_batch)
        value_loss.backward()
        self.critic_optim.step()

        self.actor.zero_grad()

        policy_loss = -self.critic([
            torch.from_numpy(state0_batch),
            self.actor(torch.from_numpy(state0_batch))
        ])

        policy_loss = policy_loss.mean()
        policy_loss.backward()
        self.actor_optim.step()

        soft_update(self.actor_target, self.actor, self.tau)
        soft_update(self.critic_target, self.critic, self.tau)

    def load_weights(self, output, step):
        if output is None: return

        self.actor.load_state_dict(
            torch.load(f'{output}/actor{step}.pkl')
        )

        self.critic.load_state_dict(
            torch.load(f'{output}/critic{step}.pkl')
        )


    def save_model(self, output, step):
        torch.save(
            self.actor.state_dict(),
            f'{output}/actor{step}.pkl'
        )
        torch.save(
            self.critic.state_dict(),
            f'{output}/critic{step}.pkl'
        )
