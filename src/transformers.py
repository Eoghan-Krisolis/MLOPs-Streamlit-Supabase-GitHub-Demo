import numpy as np
import pandas as pd


def clamp_age(x):
    return np.clip(x, 18, 100)


def clamp_motor_value(x):
    return np.clip(x, 0, 100000)


def fix_gender(df: pd.DataFrame):
    return df.replace({"f": "female", "m": "male"})
