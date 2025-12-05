# This file contains the options that you should modify to solve Question 2

def question2_1():
    #TODO: Choose options that would lead to the desired results 
    return {
        "noise": 0,
        # < 1 that the future rewards are almost zero
        "discount_factor": 0.5,
        # not so bad that it doen't care to terminate with -10
        "living_reward": -1
    }

def question2_2():
    # TODO: Choose options that would lead to the desired results
    return {
        "noise": 0.3,  # moderate randomness — makes risky shortcuts less appealing
        "discount_factor": 0.4,  # makes it prefer near +1 over far +10
        "living_reward": -0.1,  # small negative to encourage reaching a terminal (but not rush)
    }

def question2_3():
    #TODO: Choose options that would lead to the desired results
    return {
        "noise": 0,
        # the value decays slightly that it wants to get the +10 as soon as possible
        "discount_factor": 0.90,
        "living_reward": 0
    }

def question2_4():
    #TODO: Choose options that would lead to the desired results
        return {
        # actions are noisy so it will choose the action that'll make it avoid risk by any mean
        "noise": 0.2,
        # future rewards are not reduced so it aims to reach the max final reward (+10)
        "discount_factor": 1,
        # small negative penalty that it will choose 10 over 1
        "living_reward": -0.1
    }

def question2_5():
    #TODO: Choose options that would lead to the desired results
    return {
        "noise": 0,
        "discount_factor": 1,
        # rewards are positive that it avoids any terminal forever collecting rewards
        "living_reward": 5
    }

def question2_6():
    #TODO: Choose options that would lead to the desired results
    return {
        "noise": 0,
        "discount_factor": 1,
        # any movement is so paiful that it wants to terminate as soon as possible
        "living_reward": -20
    }
