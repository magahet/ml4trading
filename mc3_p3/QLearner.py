"""
Template for implementing QLearner  (c) 2015 Tucker Balch
"""

import numpy as np
import random as rand


class QLearner(object):

    def __init__(self,
                 num_states=100,
                 num_actions=4,
                 alpha=0.2,
                 gamma=0.9,
                 rar=0.5,
                 radr=0.99,
                 dyna=0,
                 verbose=False):

        self.verbose = verbose
        self.num_actions = num_actions
        self.alpha = alpha
        self.gamma = gamma
        self.rar = rar
        self.radr = radr
        self.dyna = dyna
        self.s = 0
        self.a = 0
        self.Q = np.random.uniform(-1.0, 1.0, (num_states, num_actions))

    def querysetstate(self, s):
        """
        @summary: Update the state without updating the Q-table
        @param s: The new state
        @returns: The selected action
        """
        self.s = s
        action = self.get_action(s)
        if self.verbose:
            print "s =", s, "a =", action
        return action

    def query(self, s_prime, r):
        """
        @summary: Update the Q table and return an action
        @param s_prime: The new state
        @param r: The ne state
        @returns: The selected action
        """
        self.Q[self.s, self.a] = (
            (1 - self.alpha) * self.Q[self.s, self.a] +
            self.alpha * (r + self.gamma * self.Q[s_prime, self.get_action(s_prime)])
        )

        action = self.get_action(s_prime, self.rar)

        # decay random action rate by radr
        self.rar *= self.radr

        if self.verbose:
            print "s =", s_prime, "a =", action, "r =", r

        # save state and action to update Q on next query
        self.s = s_prime
        self.a = action
        return action

    def get_action(self, s, rar=0):
        if rand.random() < rar:
            # select random action
            return rand.randint(0, self.num_actions - 1)
        else:
            # select action with max reward in Q
            return np.argmax(self.Q[s])


if __name__ == "__main__":
    print "Remember Q from Star Trek? Well, this isn't him"
