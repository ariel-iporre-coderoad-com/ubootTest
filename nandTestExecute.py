import starflex
import threading
import datetime
import json
import pandas as pd
import os

ips = [
    '10.100.154.51',
    '10.100.154.52',
    '10.100.154.53',
    '10.100.154.54',
    '10.100.154.55',
    '10.100.154.56',
    '10.100.154.57',
    '10.100.154.58',
    #'10.100.154.59',
    '10.100.154.60',
    '10.100.154.62']
clients = [starflex.star_client(ip) for ip in ips]
if not os.path.exists("./history.csv"):
    # path exists
    print "file don't exists"
    file = open('history.csv', 'w+')
    [file.write(',' + str(ip)) for ip in ips]
    file.write('\n')
    file.close()
else:
    print "file exists do nothing"


def captureCode(client):
    try:
        # code = '100'
        # code = str(json.loads(client.get_msg(end_point='info'))['webServerVersion'])
        code = str(json.loads(client.put_msg(end_point='checkNAND'))['nandCheckCode'])
    except Exception, e:
        print e
        return "Error"
    return "C" + code


def readPickle():
    try:
        return pd.read_pickle('history.pickle')
    except Exception, e:
        print e
        return pd.read_csv('history.csv', index_col=0)


class Repeater:
    def __init__(self):
        time0 = datetime.datetime(2017, 7, 26, 18, 18, 50, 78915)
        time1 = datetime.datetime(2017, 7, 26, 19, 16, 00, 78915)
        time2 = datetime.datetime(2017, 7, 26, 21, 16, 10, 78915)
        time3 = datetime.datetime(2017, 7, 26, 23, 44, 20, 78915)
        time4 = datetime.datetime(2017, 7, 26, 1, 16, 30, 78915)
        time5 = datetime.datetime(2017, 7, 26, 3, 16, 40, 78915)
        time6 = datetime.datetime(2017, 7, 26, 5, 16, 50, 78915)
        time7 = datetime.datetime(2017, 7, 26, 6, 17, 0, 78915)
        time8 = datetime.datetime(2017, 7, 26, 7, 17, 0, 78915)
        time9 = datetime.datetime(2017, 7, 26, 8, 17, 0, 78915)
        time10 = datetime.datetime(2017, 7, 26, 9, 17, 0, 78915)
        time11 = datetime.datetime(2017, 7, 26, 10, 17, 0, 78915)
        time12 = datetime.datetime(2017, 7, 26, 11, 17, 0, 78915)
        time13 = datetime.datetime(2017, 7, 26, 12, 17, 0, 78915)
        time14 = datetime.datetime(2017, 7, 26, 13, 17, 0, 78915)
        time15 = datetime.datetime(2017, 7, 26, 14, 17, 0, 78915)
        time16 = datetime.datetime(2017, 7, 26, 15, 17, 0, 78915)
        time17 = datetime.datetime(2017, 7, 26, 16, 17, 0, 78915)
        time18 = datetime.datetime(2017, 7, 26, 17, 17, 0, 78915)

        self.aDay = datetime.timedelta(days=1)
        self.times = [time0, time1, time2, time3, time4, time5, time6, time7, time6, time7, time8, time9, time10,
                      time11, time12, time13, time14, time15, time16, time17, time18]

    def executeTest(self):
        # response = json.loads(client.put_msg(end_point='/checkNAND'))
        # print "Response Message: " + str(response['nandCheckCode'])
        # codes = [random.random(), random.random()]
        codes = {client.host: captureCode(client) for client in clients}
        print "Codes: " + str(codes)
        # df = pd.read_csv('history.csv', index_col=0)
        df = readPickle()
        newRow = pd.DataFrame(codes, index=[datetime.datetime.now()])
        df = df.append(newRow)
        df.to_csv('history.csv')
        df.to_pickle('history.pickle')
        print df

    def addTimeToDatetime(self, increment):
        self.times = map(lambda t: t + increment, self.times)
        pass

    def nextExecutionTimeCalculator(self):
        current = datetime.datetime.now()
        deltas = filter(lambda x: x > 0, [(t - current).total_seconds() for t in self.times])
        print deltas
        if len(deltas) == 0:
            self.addTimeToDatetime(self.aDay)
            return 0
        else:
            print "The next acction will be executed in: " + str(min(deltas))
            # threading.Timer(min(deltas), self.executeTest)
            # threading.Timer(min(deltas), self.repeatAction)
            return min(deltas)


def repeatedAction():
    repeater = Repeater()
    nextTime = 0
    while nextTime == 0:
        nextTime = repeater.nextExecutionTimeCalculator()

    threading.Timer(nextTime, repeater.executeTest).start()
    threading.Timer(nextTime, repeatedAction).start()


repeatedAction()
while 1:
   pass
# repeater = Repeater()
# repeater.executeTest()
