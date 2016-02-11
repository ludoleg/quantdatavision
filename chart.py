import numpy as np
import matplotlib.pyplot as plt
from math import *

import StringIO

def GenerateChart(blobfile):
    angle, diff = np.loadtxt(blobfile, unpack=True)
    plt.title("Cristallography Mining Data")
    plt.plot(diff)
    plt.ylabel('Diff')

    ludo_rv = StringIO.StringIO()
    plt.savefig(ludo_rv, format="png")
    plt.clf()
    return ludo_rv


