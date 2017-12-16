# The smooth function is from scipy-cookbook:
#   http://scipy-cookbook.readthedocs.io/index.html
import scipy
import numpy as np
import matplotlib.pyplot as plt

from os.path import join

import obspy
from obspy import UTCDateTime

from obspy.signal.cross_correlation import correlate
from scipy.signal import correlate as corr

# parameter setting

dataDir = '/home/val/hard/science/data/Tolbachik/Tolbachik_days/Unit_87_028_A2'

# fileName = '/home/val/projects/corr/resources/data/20141123.mseed'
# fileName = os.path.abspath(join(homeDir, dataDir, '20141123.mseed'))

recsToRead = ['20140901.mseed', '20140902.mseed', '20140902.mseed', '20140903.mseed', '20140904.mseed',
              '20140905.mseed', '20140906.mseed', '20140907.mseed']

# year = 2014
# month = 11
# day = 23
# begin = UTCDateTime(year, month, day, 0, 0, 0)
# end = UTCDateTime(year, month, day, 23, 0, 0)

minLPEFreq = 1.0
maxLPEFreq = 5.0

downsapleFactor = 5

# create stream
streamToProcess = obspy.read(join(dataDir, recsToRead[0]))
for irec in range(1, len(recsToRead)):
    print('reading: ', recsToRead[irec])
    streamToProcess += obspy.read(join(dataDir, recsToRead[irec]))

print('start merging')
streamToProcess.merge(method=1, fill_value='interpolate')

# filtering in the interval for low-period events [1,5] Hz
print('start filtering')
filtered_trace = streamToProcess[0].copy()
filtered_trace.filter('bandpass', freqmin=minLPEFreq, freqmax=maxLPEFreq, corners=4, zerophase=True)

print('start downsampling')
filtered_trace.decimate(factor=downsapleFactor)

print('start enveloping')
envelopedTrace = filtered_trace.copy()
envelopedTrace.data = obspy.signal.filter.envelope(filtered_trace.data)
intervalToSmoothInSec = 20

print('start smoothing')
pointsToSmooth = ((intervalToSmoothInSec * filtered_trace.stats.sampling_rate) / 2) * 2 + 1
smoothed_data = scipy.signal.\
    savgol_filter(envelopedTrace.data, pointsToSmooth, polyorder=3, mode='constant')

print('start selection')
# find impulsive signals (which have envelope values greater than threshold)
threshold = 2.0 * np.average(smoothed_data)
leftEdge = 0
rightEdge = 0

eventIndexes = []  # contains indexes of LPE events in the enveloped trace

ii = 0  # current index
while ii < len(smoothed_data):
    if smoothed_data[ii] >= threshold:
        leftEdge = ii
        # find end of positive sequence
        while ii < len(smoothed_data) and smoothed_data[ii] >= threshold:
            ii = ii + 1
        rightEdge = ii - 1

        eventIndexes.append(int((leftEdge + rightEdge) / 2))
    ii = ii + 1

print('start cutting to list of events')
dt = 37.5  # time lenght of LPE event in seconds
di = int(dt / 2.0 * filtered_trace.stats.sampling_rate)

events = []
for curEventIndex in eventIndexes:
    filteredTraceEventIndex = curEventIndex
    if filteredTraceEventIndex - di < 0 or filteredTraceEventIndex + di > len(filtered_trace.data):
        continue

    events.append(filtered_trace.data[filteredTraceEventIndex - di: filteredTraceEventIndex + di])

# events = [np.array([0, 1, 1, 0]), np.array([1., 2., 0., 0.]), np.array([0., 1., 1., 0.])]

print('start cross-correlation ', len(events), 'x', len(events), ' events')
eventEnergy = np.zeros(len(events))
for ii in range(len(events)):
    ev = events[ii]
    eventEnergy[ii] = sum(ev[jj] * ev[jj] for jj in range(len(ev)))

for ii in range(10, 12):
    plt.plot(events[ii])
    plt.show()

crossCorrMacrix = np.zeros((len(events), len(events)))

ccThreshold = 0.44

for ii in range(len(events)):
    if ii % 100 == 0: print('calculating ', ii, 'th raw')
    for jj in range(len(events)):
        curCCValue = max(np.correlate(events[ii], events[jj])) / (eventEnergy[ii] * eventEnergy[jj]) ** 0.5
        if curCCValue > ccThreshold:
            crossCorrMacrix[ii, jj] = curCCValue
        else:
            crossCorrMacrix[ii, jj] = 0.0
plt.imshow(crossCorrMacrix)
plt.show()

familyNumber = 5
minFamilyMemberCount = 6

sumCC = np.sum(crossCorrMacrix, axis=0)
print(sumCC)
maxCCIndexes = sumCC.argsort()[-familyNumber:][::-1]

eventFamilies = []

for ii in maxCCIndexes:
    eventRaw = crossCorrMacrix[ii, :]
    groupCCIndexes = eventRaw.argsort()[-minFamilyMemberCount:][::-1]
    eventFamily = []

    for jj in groupCCIndexes:
        if crossCorrMacrix[ii, jj] > 0:
            eventFamily.append(events[jj])

    eventFamilies.append(eventFamily)

print('families count: ', len(eventFamilies))
for family in eventFamilies:
    print(len(family))
    for ev in family:
        lines = plt.plot(ev)
        plt.setp(lines, 'linewidth', '0.5')
        plt.show()



# dataFromSmooth = smooth(envelopedTrace.data, pointsToSmooth, 'flat')
# print(len(dataFromSmooth))


# # plotting
# traceToPlot = envelopedTrace
# t = np.arange(0, traceToPlot.stats.npts / traceToPlot.stats.sampling_rate, traceToPlot.stats.delta)
# plt.subplot(211)
#
# plt.figure(dpi=300)
# l1 = plt.plot(t, smoothed_data,
#               t, np.ones(len(t)) * averageValue,
#               t, np.ones(len(t)) * 1.7 * averageValue)
# plt.setp(l1, linewidth=0.2)
# plt.ylim((0, 10000))
# plt.ylabel('Raw Data')
# # plt.show()
#








































