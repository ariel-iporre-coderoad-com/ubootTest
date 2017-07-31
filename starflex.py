import requests
import time
import json


class star_client:
    def __init__(self, host, port='80'):
        self.host = host
        self.port = port
        self.tags = {}
        self.rounds = 0
        self.external_break = False

    @staticmethod
    def build_json(data):
        '''
        Builds a dummy json

        :param data:
        :return:
        '''
        print " sending data:" + data
        json = '{ "data1": \"' + data + '\"}'
        return json

    def post_msg(self, end_point='/', message='{}'):
        '''
        post any messge to an enpoing
        :param message: messsage string to send to endpoint
        :param end_point: default value is root '/'
        :return:
        '''
        json = self.build_json(message)
        print '=======>  json: ' + str(json)

        if not (end_point.startswith('/')):
            end_point = '/' + end_point

        if self.port.__eq__('80'):
            url = 'http://' + self.host + end_point
        else:
            url = 'http://' + self.host + ':' + self.port + end_point
        print "==> URL : " + url


        headers = {#'Connection ': 'keep-alive',
                   # 'Content-Length': '170',
                   'Content-Type': 'application/json',
                   }

        r = requests.post(url, data=None, headers=headers)
        print 'Status code: ' + str(r.status_code)
        print 'status text:  ' + str(r.text)

    def put_msg(self, msg=None, end_point='/'):
        '''
        puts someting to an endpoint
        :param msg: this is optional body to sent in the put request
        :param end_point: default value
        :return:
        '''
        if not (end_point.startswith('/')):
            end_point = '/' + end_point

        if self.port.__eq__('80'):
            url = 'http://' + self.host + end_point
        else:
            url = 'http://' + self.host + ':' + self.port + end_point
        print "URL : " + url
        r = requests.put(url)
        print r.status_code
        print r.text
        return  r.text

    def del_msg(self, end_point='/'):
        '''
        Deletet post action to kill a process in the starflex
        :param end_point:
        :return:
        '''
        if not (end_point.startswith('/')):
            end_point = '/' + end_point

        if self.port.__eq__('80'):
            url = 'http://' + self.host + end_point
        else:
            url = 'http://' + self.host + ':' + self.port + end_point
        print "URL : " + url
        r = requests.delete(url)
        print r.status_code
        print r.text

    def get_msg(self, end_point='/', verbose=False):
        '''
        simple get to read endpoint
        :param verbose:
        :param end_point: path to resource
        :return: nothing
        '''
        if not (end_point.startswith('/')):
            end_point = '/' + end_point

        if self.port.__eq__('80'):
            url = 'http://' + self.host + end_point
        else:
            url = 'http://' + self.host + ':' + self.port + end_point


        r = requests.get(url, stream=True)

        if verbose:
            print "URL : " + url
            print r.status_code


        return r.text

    def listen_during(self, time_window, end_point='/', rounds=0):
        '''
        listen an endpoint for a given period of time
        :param time_window: period of time waitn got. notice if time window is zero means infinity
        :param end_point:
        :param rounds:
        :return:
        '''
        if not (end_point.startswith('/')):
            end_point = '/' + end_point

        if self.port.__eq__('80'):
            url = 'http://' + self.host + end_point
        else:
            url = 'http://' + self.host + ':' + self.port + end_point
        print "URL : " + url
        r = requests.get(url, stream=True)
        print 'status code      : ' + str(r.status_code)
        print 'waiting time: ' + str(time_window)
        self.start_listening(r.iter_lines(), rounds, time_window)
        r.close()

    def start_listening(self, iterable, rounds, time_window):
        '''
        Consumes iterable connected to an starflex reader
        :param iterable:
        :param rounds:
        :param time_window:
        :return:
        '''
        print str(iterable)

        t0 = time.time()

        ## initialize list of tags and round count
        self.rounds = rounds
        self.tags = {}
        sequence_number = 0
        last_sequence_number = 0
        lost = 0
        with open('start_stream.txt', 'a') as f:
            print 'process started...'
            for line in iterable:
                # filter out keep-alive new lines
                # notice if time window is zero means infinity
                current_time = time.time() - t0 if time_window > 0 else -1
                # print 'current time:  ' + str(current_time)
                if time_window < 0 and self.external_break:
                    print 'external break' + str(self.external_break)
                    self.external_break = False
                    break

                if time_window < current_time:
                    print 'time up : ' + str(current_time)
                    break
                if line:
                    decoded_line = line.decode('utf-8')
                    # print '---------> decoded_line : ' + decoded_line
                    # if it a json payload
                    # print 'It is an instance of an array: ' +  str(isinstance(decoded_line,list))
                    if decoded_line.startswith("data: "):
                        # print "====>>>   decoded_line[6:]" + str(decoded_line[6:])
                        x = json.loads(decoded_line[6:])  # decodes json
                        if not isinstance(x,list):
                            last_sequence_number = sequence_number;
                            if x.has_key("seqNum"):
                                sequence_number = x['seqNum']
                            else:
                                sequence_number = "no attribute"
                            self.decode_sse_item(x)
                            if last_sequence_number == 0 & ~(sequence_number == 0):
                                print "=====>>First sequence number : " + str(sequence_number)
                            elif sequence_number > last_sequence_number + 1:
                                lost += sequence_number - last_sequence_number -1;
                                print "lost sequence: " + str(lost)
                        else:
                            for xs in x:
                                self.decode_subs_item(xs)

                    f.write(decoded_line + "\n")
                    # print decoded_line
        print 'time ended'
        self.summary()

    def summary(self):
        summary = '========================= \n'
        summary += '========================= \n'
        summary += '        Summary   \n'
        summary += '========================= \n'
        summary += '========================= \n'
        summary += 'Total rounds: ' + str(self.rounds) + ' \n'
        summary += 'List of tags: ' + str(self.tags) + ' \n'
        summary += 'Unique: ' + str(len(self.tags)) + ' \n'
        return summary

    def decode_sse_item(self, x):
        # print 'x item: ' + str(x)
        # if it is a new round counter increments
        if x['type'] == "RoundStart":
            self.rounds += 1

        # if it is a tag data increment counter in tags' dictionary
        if x['type'] == "TagReadData":
            # print('JSON loads type tagreaddata:  ' + str(x))
            print 'Round: ' + str(self.rounds)
            print 'unique tags: ' + str(len(self.tags))
            # the tag ID is found in the data field
            tag_key = x['data'][6:-4]
            # if the tags dict contains the key then
            # we increment counter
            if self.tags.has_key(tag_key):
                cnt = self.tags.get(tag_key)
                self.tags[tag_key] = cnt + 1
            else:
                # however if
                self.tags[tag_key] = 1
                # print tags
        return



    def decode_subs_item(self, xs):
        self.rounds +=1
        print('JSON loads type tagreaddata:  ' + str(xs))
        # the tag ID is found in the data field
        tag_key = xs['data'][6:-4]
        # if the tags dict contains the key then
        # we increment counter
        if self.tags.has_key(tag_key):
            cnt = self.tags.get(tag_key)
            self.tags[tag_key] = cnt + 1
        else:
            # however if
            self.tags[tag_key] = 1
            # print tags
        return

    def wait_first_round(self, time_window, end_point='/'):
        '''
        Waits for first round message and then starts to read the stream
        :param time_window: time period where it listens the messages
        :param end_point:
        :return:
        '''
        if not (end_point.startswith('/')):
            end_point = '/' + end_point

        if self.port.__eq__('80'):
            url = 'http://' + self.host + end_point
        else:
            url = 'http://' + self.host + ':' + self.port + end_point
        print "URL : " + url
        r = requests.get(url, stream=True)
        print r.status_code

        print 'Waiting for round....'
        iterable = r.iter_lines()
        for line in iterable:
            # filter out keep-alive new lines
            if line:
                decoded_line = line.decode('utf-8')
                # if it a json payload
                if decoded_line.startswith("data: "):
                    print "====>>>   decoded_line[6:]" + str(decoded_line[6:])
                    x = json.loads(decoded_line[6:])  # decodes json
                    # if it is a new round counter increments
                    if x['type'] == "RoundStart":
                        print 'Found first round.'
                        break
        if time_window > 0:
            self.start_listening(iterable=iterable, rounds=1, time_window=time_window)
        return iterable

    def stop_listening(self):
        self.external_break = True

