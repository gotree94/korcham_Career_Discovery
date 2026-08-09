# !/usr/bin/env python3
import math

ROUND_LENGTH = 10 # cm. wheel round length
ROUND_ENCODER_RATIO = 1 # Round per signal

class Encoder_to_odom:
    def __init__(self):
        pass
    def calc_vector(self, w1_delta_enc, w2_delta_enc, w3_delta_enc):
        x_vec = 0
        y_vec = 0
        w_degree = 0

        w1_y_vel = math.sin(math.radians(60)) * ROUND_LENGTH *(w1_delta_enc/ROUND_ENCODER_RATIO)
        w1_x_vel = math.cos(math.radians(60)) * ROUND_LENGTH *(w1_delta_enc/ROUND_ENCODER_RATIO)
        w2_y_vel = (-1) * math.cos(math.radians(60)) * ROUND_LENGTH *(w2_delta_enc/ROUND_ENCODER_RATIO)
        w2_x_vel = math.sin(math.radians(60)) * ROUND_LENGTH *(w2_delta_enc/ROUND_ENCODER_RATIO)
        w3_x_vel = (-1) * math.sin(ROUND_LENGTH *(w3_delta_enc/ROUND_ENCODER_RATIO))

        
