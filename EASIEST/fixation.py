prev = "empty"

import numpy as np
from collections import Counter

# Data has these values :  X, and Y coordinates and timestamps.
x = 0
y = 1
timestamp = 2

# analyze eye movements in terms of fixations  and saccades (rapid movements between fixations).
"""
The analysis of fixations and saccades requires some form of fixation identification: That is, the
translation from raw eye-movement data points to fixation
locations (and implicitly the saccades between them) on the
visual display.

Fixation identification significantly reduces
the size and complexity of the eye-movement protocol,
removing raw saccade data points and collapsing raw fixation
points into a single representative tuple. This reduction is
useful for at least two reasons. First, little or no visual
processing can be achieved during a saccade [6], and thus the
actual paths traveled during saccades are typically irrelevant for
many research applications. Second, smaller eye movements
that occur during fixations, such as tremors, drifts, and flicks
[1, 4], often mean little in higher-level analyses.
"""

""" 
Why we use Velocity-Threshold-Algorithms

The simplest of the identification methods to understand and implement.

I-VT is a velocity-based method that separates fixation and saccade points based on their point-to-point velocities
The velocity values profiles which values are fixation or which values are saccade point.

For example: 
low velocities for fixations (i.e., <100 deg/sec), and high velocities (i.e., >300 deg/sec)for saccades

"""


def ivt(data, v_threshold):
    data = np.array(data)

    times = data[:, timestamp]  # All time values.

    ts = []

    for t in times:
        ts.append(float(t) / 1000.0)  # converts each time stamp from milliseconds to seconds

    times = ts

    Xs = data[:, x]  # x coordinates
    Ys = data[:, y]  # y coordinates

    difX = []
    difY = []
    tdif = []

    for i in range(len(data) - 1):
        difX.append(float(Xs[i + 1]) - float(
            Xs[i]))  # The difference in the X coordinate between the current and the next point.
        difY.append(float(Ys[i + 1]) - float(
            Ys[i]))  # The difference in the Y coordinate between the current and the next point.
        tdif.append(
            float(times[i + 1]) - float(times[i]))  # The difference in time between the current and the next point.

    dif = np.sqrt(np.power(difX, 2) + np.power(difY, 2))  # computes the Euclidean distance  in pix
    velocity = dif / tdif  # calculates the velocity of each movement pix/sec

    mvmts = []  # for fixation grouping

    for v in velocity:
        if (v < v_threshold):  # LOW FREQUENCY, so Fixation

            mvmts.append(1)

        else:
            mvmts.append(0)  # It is new fixation

    fixations = []
    fs = []  # (it used to store indices of consecutive fixations)

    for m in range(len(mvmts)):
        if (mvmts[m] == 0):  # End of fixation group
            if (len(fs) > 0):
                fixations.append(fs)
                fs = []

        fs.append(m)
    if (len(fs) > 0):  # If there is a fixation in the last index of list
        fixations.append(fs)

    # print fixations
    centroidsX = []
    centroidsY = []
    time0 = []
    time1 = []
    fixation_counts = []

    for f in fixations:  # [ [0,1,2,3,4]    [5,6,7]  [8]   ]
        cX = 0
        cY = 0

        if (len(f) == 1):  # Fixation group has a 1 element.
            i = f[0]
            cX = (float(data[i][x]) + float(data[i + 1][x])) / 2.0
            cY = (float(data[i][y]) + float(data[i + 1][y])) / 2.0
            t0 = float(data[i][timestamp])
            t1 = float(data[i + 1][timestamp])  # Next point's first time look.

        else:
            t0 = float(data[f[0]][timestamp])  # Timestamp of the first element of array = First Look
            t1 = float(data[f[len(f) - 1] + 1][timestamp])

            for e in range(len(f)):
                cX += float(data[f[e]][x])
                cY += float(data[f[e]][y])

            cX += float(data[f[len(f) - 1] + 1][x])  # add a degree of flexibility in calculating the fixation groups.
            cY += float(data[f[len(f) - 1] + 1][y])

            cX = cX / float(len(f) + 1)
            cY = cY / float(len(f) + 1)

        centroidsX.append(cX)
        centroidsY.append(cY)
        fixation_counts.append(len(f))
        time0.append(t0)
        time1.append(t1)
    fixation_total = []

    total = 0
    for i in fixation_counts:
        total += i

    for i in range(0, len(centroidsX)):
        fixation_total.append(
            (centroidsX[i], centroidsY[i], time0[i] / 1000, (time1[i] - time0[i]) / 1000, fixation_counts[i]))

    return fixation_total  # Return X,Y,FirstLook,Duration,Fixation_Count


def idt(data, dis_threshold, dur_threshold):
    data = np.array(data)
    window_range = [0, 0]

    current = 0  # pointer to represent the current beginning point of the window
    last = 0
    # final lists for fixation info
    centroidsX = []
    centroidsY = []
    time0 = []
    time1 = []
    fixation_counts = []

    while current < len(data):

        t0 = float(data[current][timestamp])  # beginning time
        t1 = t0 + float(dur_threshold)  # time after a min. fix. threshold has been observed

        for r in range(current, len(data)):
            if float(data[r][timestamp]) >= t0 and float(data[r][timestamp]) <= t1:
                last = r  # this will find the last index still in the duration threshold

        window_range = [current, last]

        # now check the dispersion in this window
        dispersion = get_dispersion(data[current:last + 1])

        if dispersion <= dis_threshold:
            # add new points
            while dispersion <= dis_threshold and last + 1 < len(data):
                last += 1
                window_range = [current, last]
                dispersion = get_dispersion(data[current:last + 1])

            # dispersion threshold is exceeded
            # fixation at the centroid [current,last]

            cX = 0
            cY = 0

            for f in range(current, last + 1):
                cX += float(data[f][x])
                cY += float(data[f][y])

            cX = cX / float(last - current + 1)
            cY = cY / float(last - current + 1)

            t0 = float(data[current][timestamp])
            t1 = float(data[last][timestamp])

            centroidsX.append(cX)
            centroidsY.append(cY)
            time0.append(t0)
            time1.append(t1)
            fixation_counts.append(len(data[current:last + 1]))

            current = last + 1  # this will move the pointer to a novel window

        else:
            current += 1  # this will remove the first point
            last = current  # this is not necessary

    fixation_total = []

    for i in range(len(centroidsX)):
        fixation_total.append((centroidsX[i], centroidsY[i], time0[i] / 1000, (time1[i] - time0[i]) / 1000, fixation_counts[i]))

    return fixation_total


def get_dispersion(points):
    argxmin = np.min(points[:, x].astype(float))
    argxmax = np.max(points[:, x].astype(float))

    argymin = np.min(points[:, y].astype(float))
    argymax = np.max(points[:, y].astype(float))

    dispersion = ((argxmax - argxmin) + (argymax - argymin)) / 2


    return dispersion

