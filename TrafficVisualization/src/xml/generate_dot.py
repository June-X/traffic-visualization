'''
Created on Mar 14, 2010

@author: lzcarl

1. merge two log files with time sequence: key-logger.txt from tlogger and sniff from sniff.py
2. extract all the logs within a range and classify them into clusters
user-triggered event : {generated URLs}
3. generate dot file
'''

import sys
import time
import string
import os
from datetime import datetime
from urlparse import urlparse

def process_log(filename, list, type):
    f = open(filename, "r")
    key_log_content = f.readlines()
    for i in range(len(key_log_content)):
        line = key_log_content[i]
        p = line.split()
        if len(p) < 3:
            continue
        if type == "key":
            log_time = p[0] + " " + p[1]
            if not p[2].startswith("URL:") or len(p) < 4:
                continue
            url = p[3]
            if not [log_time, url] in list:
                list.append([log_time, url, ""])
        elif type == "sniff":
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

def process_key(filename, list, type):
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
    	    log_time = p[0] + " " + p[1]
    	    # load a new URL
    	    if p[2].find('"load_start"') >= 0:
                url = find_value(p[2], "href")
                load_time = log_time
                load_url = url
                # sometimes load_start will load some pages not triggered by user
                # Only the load_start followed by location_change is considered triggered by user
            elif p[2].find('"LocationChange"') >= 0:
                url = find_value(p[2], "href")
                if url <> "about:blank":
                    result_list.append([load_time, load_url, []])
                    current_index = len(list) - 1
            elif p[2].find('"LINK_CLICK"') >= 0:
                click = find_value(p[2], "href")
                result_list[current_index][2].append([log_time, "CLICK", click])
            elif p[2].find('"keypress"') >= 0:
                key = find_value(p[2], "keys")
                if len(result_list) > 0:
                    result_list[current_index][2].append([log_time, "KEYPRESS", key])
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
    process_key(key_log, key_log_list, "key")
    process_log(sniff_log, sniff_log_list, "sniff")
    chop_list_by_time(start, end, key_log_list)
    chop_list_by_time(start, end, sniff_log_list)    
    # correlate sniff_log_list to key_log_list
    sniff_len = len(sniff_log_list)
    key_len = len(key_log_list)
    j_start = 0
    for i in range(key_len - 1):
        merged_list.append({"label":"Website " + str(i), "u":"u" + str(i),\
                            "ui":"ui" + str(i), "c":"cluster" + str(i), "f":"f0",\
                            "url":cut_url(key_log_list[i][1]), "time":key_log_list[i][0],\
                            "events":key_log_list[i][2], "sub":[]})
        for j in range(j_start, sniff_len):
            if time_compare(sniff_log_list[j][0], key_log_list[i + 1][0]) in ["bigger", "equal"]:
                j_start = j
                break
            if time_compare(sniff_log_list[j][0], key_log_list[i][0]) in ["bigger", "equal"]:
                sniff_log_list[j][2] = key_log_list[i][0]
                sub_url = cut_url(sniff_log_list[j][1])
                sub_time = sniff_log_list[j][0]
                need_sub_url = True
                for k in merged_list[i]["sub"]:
                    if sub_url == k["sub_url"]:
                        need_sub_url = False
                        break
                if need_sub_url:
                    merged_list[i]["sub"].append({"sub_time":sub_time, "sub_url":sub_url, "f":"f" + str(j - j_start + 1)})
                        
    
    i = key_len - 1
    merged_list.append({"label":"Website " + str(i), "u":"u" + str(i),\
                        "ui":"ui" + str(i), "c":"cluster" + str(i), "f":"f0",\
                        "url":cut_url(key_log_list[i][1]), "time":key_log_list[i][0],\
                        "events":key_log_list[i][2], "sub":[]})
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
    
    print merged_list

def gen_subgraph(item):
    begin = 'subgraph %s{\n\tstyle=filled;\n\tcolor=white;\n\t\n\t' % (item["c"])
    urls = "<%s>%s" % (item["f"], item["url"])
    for i in item["sub"]:
        url = "<%s>%s | " % (i["f"], i["sub_url"])
        urls = url + urls
    u = '%s [label = "%s"\n\t\tshape="record"];\n\t' %(item["u"], urls)
    content = '%s%slabel = "%s";\n\t}\n\t\n\t' % (begin, u, item["label"])
    return content

def gen_ui(item):
    ui_list = ""
    for i in range(len(item["events"])):
        event = item["events"][i]
        if event[1] == "CLICK":
            ui = " | <f%d>%s:%s" % (i, event[1], cut_url(event[2]))
            ui_list = ui + ui_list
        elif event[1] == "KEYPRESS":
            ui = "| <f%d>%s:%s" % (i, event[1], event[2])
            ui_list = ui + ui_list
    content = '\t%s [label = "%s"\n\t\tshape="record", color=purple];\n\n'\
        % (item['ui'], ui_list[2:], )
    return content

def gen_dot(filename, list):
    f = open(filename, "w")
    content = "Graph AS{\n\trankdir=LR\n\t"
    for item in list:
        content = content + gen_subgraph(item)
        
    con_number = len(list) * 2
    con_start = "\n\n\tstart [shape=Mdiamond];\n\tend [shape=Msquare];"
    con_list = ""
    for i in range(con_number):
        con_list += "con%d [shape=plaintext, style=filled, color=white, label="", height=.001, width=.001];\n\t" %(i)
    
    #ui = '\n\tnode [style="rounded, filled", color=purple];\n\t'
    ui = "\n\n"
    for i in range(len(list)):
        #ui += "ui%d " %(i)
        ui += gen_ui(list[i])
    #ui += ";\n\n\t"
    ui += "\n\t"
    
    con_body = "start -- con0[weight=3];\n\t"
    for i in range(con_number - 1):
        con_body += "con%d -- con%d[weight=1];\n\t" % (i, i + 1)
    con_body += "con%d -- end[weight=3];\n\n\t" % (con_number - 1)  
    
    con_end = ""
    for i in range(len(list)):
        con_end += "con%d -- %s:%s[shape =crow];\n\tcon%d -- %s[shape=crow];\n\t"\
            %(2*i, list[i]["u"], list[i]["f"], 2*i+1, list[i]["ui"])
            
    content = content + con_list + ui + con_body + con_end + "}"
    f.write(content)
    f.flush()

def write_trace(merged_list, trace):
    f = open(trace, "w")
    for main_item in merged_list:
        main_line = main_item['time'] + " VISIT " + main_item['url'] + '\n'
        f.write(main_line)
        # write sub items
        for sub_item in main_item['sub']:
            sub_line = sub_item['sub_time'] + " DOWNLOAD " + sub_item['sub_url'] + '\n'
            f.write(sub_line)
        for event_item in main_item['events']:
            event_line = event_item[0] + " " + event_item[1] + " " + event_item[2]
            f.write(event_line)
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
    gen_dot(output, merged_list)