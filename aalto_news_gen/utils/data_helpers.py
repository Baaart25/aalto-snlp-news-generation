from multiprocessing import Pool
from os import path, mkdir

import numpy as np
import pandas as pd



def make_dir_if_not_exists(directory):
    if not path.exists(directory):
        mkdir(directory)
        