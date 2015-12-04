"""
Template for implementing QLearner  (c) 2015 Tucker Balch
"""

import numpy as np
import random as rand


class Q(object):

    def __init__(self, num_states, num_actions, alpha, gamma):
        self.Q = np.random.uniform(-1.0, 1.0, (num_states, num_actions))
        self.num_actions = num_actions
        self.alpha = alpha
        self.gamma = gamma

    def update(self, s, a, s_prime, r):
        self.Q[s, a] = (
            (1 - self.alpha) * self.Q[s, a] +
            self.alpha * (r + self.gamma * self.Q[s_prime, self.query(s_prime)])
        )

    def query(self, s):
        return np.argmax(self.Q[s])


class T(object):

    def __init__(self, num_states, num_actions):
        self.Tc = np.ones((num_states, num_actions, num_states)) * 0.00001

    def update(self, s, a, s_prime):
        self.Tc[s, a, s_prime] += 1

    def query(self, s, a):
        p = self.Tc[s, a] / self.Tc[s, a].sum()
        return np.random.choice(range(len(p)), p=p)


class R(object):

    def __init__(self, num_states, num_actions, alpha):
        self.R = np.zeros((num_states, num_actions))
        self.alpha = alpha

    def update(self, s, a, r):
        self.R[s, a] = (1 - self.alpha) * self.R[s, a] + self.alpha * r

    def query(self, s, a):
        return self.R[s, a]


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
        self.num_states = num_states
        self.num_actions = num_actions
        self.rar = rar
        self.radr = radr
        self.dyna = dyna
        self.s = 0
        self.a = 0
        self.Q = Q(num_states, num_actions, alpha, gamma)
        self.T = T(num_states, num_actions)
        self.R = R(num_states, num_actions, alpha)

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
        self.Q.update(self.s, self.a, s_prime, r)

        action = self.get_action(s_prime)

        # decay random action rate by radr
        self.rar *= self.radr

        # save state and action to update Q on next query
        self.s = s_prime
        self.a = action

        if self.verbose:
            print "s =", s_prime, "a =", action, "r =", r

        if self.dyna:
            # update model of T and R
            self.T.update(self.s, self.a, s_prime)
            self.R.update(self.s, self.a, r)

            for _ in range(self.dyna):
                s = rand.randrange(self.num_states)
                a = rand.randrange(self.num_actions)
                s_prime = self.T.query(s, a)
                r = self.R.query(s, a)
                self.Q.update(s, a, s_prime, r)

        return action

    def get_action(self, s):
        if rand.random() < self.rar:
            # select random action
            return rand.randint(0, self.num_actions - 1)
        else:
            # select action with max reward in Q
            return self.Q.query(s)


if __name__ == "__main__":
    print "Remember Q from Star Trek? Well, this isn't him"
