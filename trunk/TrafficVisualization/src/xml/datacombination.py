'''
created on May 25, 2010

@author: Huijun
1. merge two log files with time sequence: "extstore.dat" and sniff generated by sniff.py
2. generate files with record format: <date><time><type><data><ip>. type={URL, KB, MC}, only when type == URL, <ip> has data, otherwise it's empty

'''

import sys
import time
import string
import os
from datetime import datetime
from urlparse import urlparse

def process_sniff(filename, list, type):
    f = open(filename, "r")
    key_log_content = f.readlines()
    for i in range(len(key_log_content)):
        line = key_log_content[i]
        p = line.split()
        if len(p) < 4:
            continue
        if type == "sniff":
            '''
            log_time = p[0] + " " + p[1]
            '''
            log_date = p[0];
            log_time = p[1];
            '''
            if not p[2].startswith("URL:") or len(p) < 4:
                continue
            '''
            ip = p[3]
            url = p[4]
            if not [log_date, log_time, ip, url] in list:
                list.append(["URL", log_date, log_time, ip, url, ""])
        elif type == "key":
            log_time = p[0] + " " + p[1][:-3]
            url = p[2].strip("[]")
            if not [log_time, url] in list:
                list.append([log_time, url, ""])
    print 'sniff', list, len(list)

# parse the tlogger log file to get the related part
def find_value(str, key):
    parts = str.split(',')
    for part in parts:
        if part.startswith('"' + key + '"'):
            value = part.split('":"')[1]
            return value[:-1]

def process_logger(filename, list, type):
    f = open(filename, "r")
    key_log_content = f.readlines()
    current_index = 0
    result_list = []
    location_list = []
    last = ""
    load_url = ""
    load_time = ""
                                  
    for i in range(len(key_log_content)):
        line = key_log_content[i]
    	p = line.split()
        if len(p) < 3:
            continue
    	if type == "key":
    	    log_date = p[0]
    	    log_time = p[1]
    	    # load a new URL
    	    if p[2].find('"load_start"') >= 0:
                url = find_value(p[2], "href")
                load_date = log_date
                load_time = log_time
                load_url = url
                # sometimes load_start will load some pages not triggered by user
                # Only the load_start followed by location_change is considered triggered by user
            elif p[2].find('"LocationChange"') >= 0:
                url = find_value(p[2], "href")
                if url <> "about:blank":
                    result_list.append(["MC", load_date, load_time, load_url])
                    current_index = len(list) - 1
            elif p[2].find('"LINK_CLICK"') >= 0:
                click = find_value(p[2], "href")
                result_list[current_index][2].append(["MC", log_date, log_time, click])
            elif p[2].find('"keypress"') >= 0:
                key = find_value(p[2], "keys")
                if len(result_list) > 0:
                    result_list[current_index][2].append(["KB", log_date, log_time, key])
    #remove the about:blank ones
    for item in result_list:
        if item[1] <> "about:blank":
            list.append(item)
    print 'key', list, len(list)

def time_compare(time1_str, time2_str):
    # return the compared result between time1 and time2
    if time1_str.find(".") == -1:
        [time1_beforems, time1_ms] = [time1_str, 0]
    else:   
        [time1_beforems, time1_ms] = time1_str.split('.')
        if len(time1_ms) == 6:
            time1_ms = time1_ms[:3]
    
    if time2_str.find(".") == -1:
        [time2_beforems, time2_ms] = [time2_str, 0]
    else:
        [time2_beforems, time2_ms] = time2_str.split('.')
        if len(time2_ms) == 6:
            time2_ms = time2_ms[:3]        
    time1 = datetime.strptime(time1_beforems, "%Y-%m-%d %H:%M:%S")
    time1 = time1.replace(microsecond = int(time1_ms))
    time2 = datetime.strptime(time2_beforems, "%Y-%m-%d %H:%M:%S")
    time2 = time2.replace(microsecond = int(time2_ms))
    if time1 > time2:
        return "bigger"
    elif time1 == time2:
        return "equal"
    else:
        return "smaller"

def chop_list_by_time(start, end, list):
    removed_items = []
    for i in list:
        if start <> "" and time_compare(i[0], start) in ["smaller"]:
            # list.remove(i)
            removed_items.append(i)
            continue
        if end <> "" and time_compare(i[0], end) in ["bigger"]:
            # list.remove(i)
            removed_items.append(i)        
            continue 
    for i in removed_items:
        list.remove(i)   
    print list, len(list)

def cut_url(url):
    # cut off the string after the second-level
    p = urlparse(url)
    # takes
    path = p[2]
    path_parts = path.split("/")
    if len(path_parts) > 1:
        return p[1] + path_parts[0] + "/" + path_parts[1]
    else:
        return p[1] + path_parts[0]

def merge(key_log, sniff_log, key_log_list, sniff_log_list, start, end, merged_list):
# merge the logs based on time
    process_logger(key_log, key_log_list, "key")
    process_sniff(sniff_log, sniff_log_list, "sniff")
    chop_list_by_time(start, end, key_log_list)
    chop_list_by_time(start, end, sniff_log_list)    
    # correlate sniff_log_list to key_log_list
    sniff_len = len(sniff_log_list)
    key_len = len(key_log_list)
    j_start = 0
    for i in range(key_len - 1):
        #write down record in key_log_list
        print key_log_list[i][0]
        '''
        if t == "MC"
            merged_list.append({"TYPE":key_log_list[i][0], "date":key_log_list[i][1],\
                            "time":key_log_list[i][2], "click":key_log_list[i][3]})
            elif key_log_list[i][0] == 'KB' 
                merged_list.append({"TYPE":key_log_list[i][0], "date":key_log_list[i][1],\
                            "time":key_log_list[i][2], "key":key_log_list[i][3]})
        '''
        #find following URL record in sniff_log_list
        for j in range(j_start, sniff_len):
            sniff_time = sniff_log_list[j][1] + " " + sniff_log_list[j][2]
            key_after_time = key_log_list[i + 1][1] + " " + key_log_list[i + 1][2]
            key_previous_time = key_log_list[i][1] + " " + key_log_list[i][2]
            if time_compare(sniff_time, key_after_time) in ["bigger", "equal"]:
                j_start = j
                break
            if time_compare(sniff_time, key_previous_time) in ["bigger", "equal"]:
                 merged_list.append({"TYPE":sniff_log_list[j][0], "date":sniff_log_list[j][1],\
                                     "time":sniff_log_list[j][2], "ip":sniff_log_list[j][3],\
                                    "url":sniff_log_list[j][4]})
            '''
                sniff_log_list[j][3] = key_log_list[i][0]
                sub_url = cut_url(sniff_log_list[j][1])
                sub_time = sniff_log_list[j][0]
                need_sub_url = True
                for k in merged_list[i]["sub"]:
                    if sub_url == k["sub_url"]:
                        need_sub_url = False
                        break
                if need_sub_url:
                    merged_list[i]["sub"].append({"sub_time":sub_time, "sub_url":sub_url, "f":"f" + str(j - j_start + 1)})
                 '''
    
    i = key_len - 1
    '''
    if key_log_list[i][0] == 'MC' 
            merged_list.append({"TYPE":key_log_list[i][0], "date":key_log_list[i][1],\
                            "time":key_log_list[i][2], "click":key_log_list[i][3]})
        elif key_log_list[i][0] == 'KB' 
            merged_list.append({"TYPE":key_log_list[i][0], "date":key_log_list[i][1],\
                            "time":key_log_list[i][2], "key":key_log_list[i][3]})

    '''
    '''
    for j in range(j_start, sniff_len):
        sniff_log_list[j][2] = key_log_list[i - 1][0]
        sub_url = cut_url(sniff_log_list[j][1])
        sub_time = sniff_log_list[j][0]
        need_sub_url = True
        for k in merged_list[i]["sub"]:
            if sub_url == k["sub_url"]:
                need_sub_url = False
                break
        if need_sub_url:
            merged_list[i]["sub"].append({"sub_time":sub_time, "sub_url":sub_url, "f":"f" + str(j - j_start + 1)})
    '''
    print merged_list

def write_trace(merged_list, trace):
    f = open(trace, "w")
    start_file = "<? xml version = \"1.0\" encoding = \"UTF-8\"? \n"
    start_events = "<events>\n"
    end_events = "</events>"
    start_line = "<event date=\">"
    end_line = "</event>"
    start_time = "\"<time>"
    end_time = "</time>"
    start_type = "<type>"
    end_type = "</type>"
    start_ip = "<ip>"
    end_ip = "</ip>"
    start_URL = "<URL>"
    end_URL = "</URL>"
    start_key = "<key>"
    end_key = "</key>"
    start_click = "<click>"
    end_click = "</click>"

    f.write(start_file)
    f.write(start_events)
    '''
    for main_item in merged_list:
        main_line = start_line + main_item['date'] + "\">" + start_time + main_item['time'] + end_time \
                    + start_type + main_item[TYPE] + end_type
        if main_item[TYPE] == 'URL'
            main_line = main_line + start_ip + main_item[ip] + end_ip + start_URL + main_item[url] + end_URL
            elif main_item[TYPE] == 'MC'
                main_line = main_line + start_click + main_item[click] + end_click
                elif main_item[TYPE] == 'KB'
                    main_line = main_line + start_key + main_item[key] + end_key

        main_line = main_line + end_line + "\n"
        f.write(main_line)
    '''
        '''
        # write sub items
        for sub_item in main_item['sub']:
            sub_line = sub_item['sub_time'] + " DOWNLOAD " + sub_item['sub_url'] + '\n'
            f.write(sub_line)
        for event_item in main_item['events']:
            event_line = event_item[0] + " " + event_item[1] + " " + event_item[2]
            f.write(event_line)
        '''
    f.write(end_events)
    f.flush()

if __name__ == '__main__':
    key_log = "extstore.dat"
    sniff_log = "sniff"
    start = ""
    end = ""
    output = "output.dot"
    trace = "trace"
    sniff_log_list = []
    key_log_list = []
    merged_list = []
    
    if len(sys.argv) > 1:
        key_log = sys.argv[1]
    if len(sys.argv) > 2:
        sniff_log = sys.argv[2]
    if len(sys.argv) > 3:
        start = sys.argv[3]
    if len(sys.argv) > 4:
        end = sys.argv[4]
    if len(sys.argv) > 5:
        output = sys.argv[5]
    if len(sys.argv) > 6:
        trace = sys.argv[6]
                
    merge(key_log, sniff_log, key_log_list, sniff_log_list, start, end, merged_list)
    write_trace(merged_list, trace)