"""
@project: Mobile Edge Offloading
@author: Md Rajib Hossen
@time: 03/15/2020
@email: mdrajib.hossen@mavs.uta.edu
"""
import itertools
import random
from collections import deque

import matplotlib.style
import numpy as np
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.utils import normalize

from environment import Environment
from lib import plotting

matplotlib.style.use('ggplot')

batch_size = 64


class DeepQLearning:
    def __init__(self, actions, state_size, lr=0.01, discount=0.9, e_greedy=0.9):
        self.actions = actions
        self.n_actions = len(self.actions)
        self.n_states = state_size
        self.lr = lr
        self.discount = discount
        self.epsilon = e_greedy
        self.optimizer = Adam(lr=0.001)
        self.experience_replay = deque(maxlen=100000)

        self.q_network = self.build_compile_model()
        self.target_network = self.build_compile_model()
        self.align_target_model()

    def build_compile_model(self):
        model = Sequential()
        # states = tf.placeholder(shape=[None, self.n_states], dtype=tf.float64)
        # self._q_s_a = tf.placeholder(shape=[None, self._num_actions], dtype=tf.float32)
        # model.add(InputLayer(input_tensor=))
        model.add(Dense(50, activation='relu', input_dim=self.n_states))
        model.add(Dense(50, activation='relu'))
        model.add(Dense(50, activation='relu'))
        model.add(Dense(self.n_actions, activation='linear'))  # linear or softmax
        # model = model(states)

        model.compile(loss='mse', optimizer=self.optimizer, metrics=['accuracy'])
        return model

    def align_target_model(self):
        self.target_network.set_weights(self.q_network.get_weights())

    def store(self, state, action, reward, n_state, terminated):
        # self.experience_replay.append((state, action, reward, n_state, terminated))
        self.experience_replay.append((state, action, reward, n_state, terminated))

    def choose_action(self, state):
        # self.check_state_exists(state)
        # action selection trade of between exploration and exploitation, explore 10% of the time
        if np.random.uniform() < self.epsilon:
            # choose best action
            q_values = self.q_network.predict(state)
            # print(q_values)
            action = np.argmax(q_values[0])
            # print(action)
        else:
            action = np.random.choice(self.actions)

        return action

    def learn(self, batch_size):

        minibatch = random.sample(self.experience_replay, batch_size)

        for state, action, reward, n_state, terminated in minibatch:
            target = self.q_network.predict(state)

            if terminated:
                target[0][action] = reward
            else:
                t = self.q_network.predict(n_state)
                target[0][action] = reward + self.discount * np.amax(t)

            self.q_network.fit(state, target, epochs=1, verbose=0)


def update(env, DQL, episodes=1000):
    ep_no = 1
    # state = env.reset()
    for episode in range(episodes):
        state = env.reset()
        state = np.asarray(state)
        state = state.reshape(1, 7)
        state = normalize(state)
        for t in itertools.count():
            print("Episode [%d] Iteration: %d" % (ep_no, t))

            action = DQL.choose_action(state)
            next_state, reward, done = env.step(action)

            stats.episode_rewards[episode] += reward
            stats.episode_lengths[episode] = t

            next_state = np.asarray(next_state)
            next_state = next_state.reshape(1, 7)
            next_state = normalize(next_state)
            DQL.store(state, action, reward, next_state, done)
            # print(state, action, reward, done)
            state = next_state

            if done:
                DQL.align_target_model()
                break

            if len(DQL.experience_replay) > batch_size:
                # print("updating")
                DQL.learn(batch_size)

        ep_no += 1
    print("complete")


if __name__ == '__main__':
    num_of_episodes = 10000

    env = Environment()

    stats = plotting.EpisodeStats(
        episode_lengths=np.zeros(num_of_episodes),
        episode_rewards=np.zeros(num_of_episodes))

    DQL = DeepQLearning(actions=list(range(env.n_actions)), state_size=7)

    update(env, DQL, episodes=num_of_episodes)

    plotting.plot_episode_stats(stats)