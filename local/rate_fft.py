import pymongo
import time
import numpy as np
import datetime
import collections
from scipy import signal


conn = pymongo.MongoClient('mongodb://128.199.118.43:27017/', username='sam',password='mongo23392399',authSource='admin',authMechanism='SCRAM-SHA-256')
db = conn['admin']

ava_rate =  collections.deque([0, 0, 0, 0, 0, 0, 0, 0, 0, 0], maxlen=10)
while 1:
    try:
        datalist = list(db.real_time.find({'time':{"$gte": datetime.datetime.now()-datetime.timedelta(seconds=10)}}))
        #datalist = list(db.real_time.find({}).sort('_id', -1).limit(1000))
        if datalist == []:
            continue
        valuelist = []
        timelist = []
        for i in datalist:
            valuelist.append(i.get('value', 0))
            timelist.append(datetime.datetime.timestamp(i.get('time', None)))
        fs = 1/(abs(timelist[-1] - timelist[0])/len(timelist))
        f = np.arange(0, fs, fs/len(timelist))
        #valuelist = signal.lfilter([1/3, 1/3, 1/3], 1, (valuelist - np.mean(valuelist)))
        value_fft = np.fft.fft(valuelist)
        x_skip = 0
        for i in f:
            if(i < 0.7):
                x_skip += 1
        value_fft = abs(value_fft)
        rate = f[np.argmax( value_fft[x_skip: int(len(value_fft)/2)] )+x_skip]*60
        ava_rate.append(rate)
        #print('fs: ', fs)
        print(np.average(ava_rate))
        #print(datalist)
        time.sleep(1)
    except Exception as e:
        if e == KeyboardInterrupt:
            break
        else:
            print(e)
            pass

print('done')