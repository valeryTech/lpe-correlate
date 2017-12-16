# This script creates one-day miniseed records
from obspy.core.utcdatetime import UTCDateTime
import os
from obspy import read
from os import listdir
from os.path import isfile, join, isdir
from time import gmtime, strftime

# change directory to the working path
workDir = "/home/user/Projects/converting_test"

# inputDir = "/media/user/extHardDisk/Tolbachik_out_seed"
# outputDir = "/media/user/extHardDisk/Tolbachik_days"
inputDir = "/home/user/Projects/converting_test/test_in"
outputDir = "/home/user/Projects/converting_test/test_out"

# get all dirs in the input dir
directories = [d for d in listdir(inputDir) if isdir(join(inputDir, d))]

# get all files in current dir
for curDir in directories:
    print("start converting files in : " + curDir)
    os.chdir(os.path.join(inputDir, curDir))
    records = [f for f in listdir(os.path.join(inputDir, curDir)) if isfile(join(inputDir, curDir, f))]
    records.sort()
    if len(records) == 0:
        break

    for month in range(1, 12 + 1):
        for day in range(1, 31 + 1):
            if (day == 31 and month in [2, 4, 6, 9, 11]) or (month == 2 and day in [29, 30, 31]):
                break
            monthDayString = str(month).zfill(2) + str(day).zfill(2)
            predecDay = str(month).zfill(2) + str(day - 1).zfill(2)
            postDay = str(month).zfill(2) + str(day + 1).zfill(2)

            recsToWrite = [rec for rec in records if rec[0:4] == monthDayString]
            predRecs = [rec for rec in records if rec[0:4] == predecDay]
            if len(predRecs) > 0:
                recsToWrite.append(predRecs[-1])

            postRecs = [rec for rec in records if rec[0:4] == postDay]
            if len(postRecs) > 0:
                recsToWrite.append(postRecs[0])

            # todo: put it in input parameters
            minimumRecordsPerDay = 3
            if len(recsToWrite) > minimumRecordsPerDay:
                stream2Write = read(join(inputDir, curDir, recsToWrite[0]))
                for irec in range(1, len(recsToWrite)):
                    stream2Write += read(join(inputDir, curDir, recsToWrite[irec]))

                if month in range(8, 12 + 1):
                    year = 2014
                else:
                    year = 2015
                dayBegin = UTCDateTime(year, month, day, 0, 0, 0)
                dayEnd = UTCDateTime(year, month, day, 23, 59, 59)

                stream2Write.merge(method=1, fill_value='interpolate')
                stream2Write = stream2Write.slice(dayBegin, dayEnd)

                name = str(year) + monthDayString + ".mseed"
                stream2Write.write(join(outputDir, curDir, name), format="MSEED")

                print(curDir, dayBegin, strftime("%Y-%m-%d %H:%M:%S", gmtime()))

    #   # first day pointer
    #     firstStream = read(join(inputDir, curDir, records[0]))
    #
    #     currentDay = firstStream[0].stats.starttime
    #
    #     dayBegin = UTCDateTime(currentDay.year, currentDay.month, currentDay.day, 0, 0, 0)
    #     dayEnd = UTCDateTime(currentDay.year, currentDay.month, currentDay.day, 23, 59, 59)
    #
    #     # position of the last read record in the list 'records'
    #     lastReadedRecord = 0
    #
    #     [lastIndex, stream2cut, endListRiched] = get_stream_to_cut(records, lastReadedRecord, dayEnd)
    #     #print(dayBegin, stream2cut[0].stats.starttime, stream2cut[0].stats.endtime)
    #
    #     name = str(dayBegin.year) + str(dayBegin.month).zfill(2) + str(dayBegin.day).zfill(2) + ".mseed"
    #
    #     stream2cut.slice(dayBegin, dayEnd).write(join(outputDir, curDir, name), format="MSEED")
    #
    #     while not endListRiched:
    #
    #         currentDay = read(join(inputDir, curDir, records[lastIndex]))[0].stats.endtime
    #
    #         dayBegin = UTCDateTime(currentDay.year, currentDay.month, currentDay.day, 0, 0, 0)
    #         dayEnd = UTCDateTime(currentDay.year, currentDay.month, currentDay.day, 23, 59, 59)
    #         [lastIndex, stream2cut, endListRiched] = get_stream_to_cut(records, lastReadedRecord, dayEnd)
    #
    #         print(curDir, dayBegin, strftime("%Y-%m-%d %H:%M:%S", gmtime()))
    #         name = str(dayBegin.year) + str(dayBegin.month).zfill(2) + str(dayBegin.day).zfill(2) + ".mseed"
    #         stream2cut.slice(dayBegin, dayEnd).write(join(outputDir, curDir, name), format="MSEED")
    #         stream2cut = 0
    #         lastReadedRecord = lastIndex
    #
    # #        gc.collect()

    print("end converting files in : " + curDir)

# stream2show.merge(method=1, fill_value='interpolate')

# stream2show.plot()
