import argparse
import json
import sys
import re
from collections import defaultdict

def parse_args():
    argument_parse = argparse.ArgumentParser(description = "Log summarization based on templates.")
    argument_parse.add_argument("-t", action = "store", dest = "templatefile", default = "./sample/access_log_template_50", help = "The template file")
    argument_parse.add_argument("-f", action = "store", dest = "logfile", default = "./sample/access_log", help = "The log file to analyze")
    argument_parse.add_argument("-p", action = "store", dest = "peeler", default = "./peeler/access_log", help = "Log file's message peeler")
    results = argument_parse.parse_args()
    templatepath = results.templatefile
    logfilepath = results.logfile
    peelerpath = results.peeler
    return templatepath, logfilepath, peelerpath

def get_peeler(peelerpath):
    with open(peelerpath, 'r') as pfin:
        line = pfin.readline()
        try:
            peeler = json.loads(line)
        except ValueError:
            print "--->Input file format error!"
            sys.exit(1)
    return peeler

def load_template(templatepath):
    template = []
    with open(templatepath, 'r') as tfin:
        json_template = json.load(tfin)
        for curr_tmp in json_template:
            template.append((curr_tmp["id"], curr_tmp["template"]))
    return template

def match_template(logfilepath, peeler, template):
    outer_delimiter = peeler["outer_delimiter"]
    inner_delimiter = peeler["inner_delimiter"]
    start = int(peeler["message_start"])
    end = peeler["message_end"]
    if end != "":
        end = int(end)
    else:
        end = None
    
    matched_count = defaultdict(int)
    matched_tokens = {}
    for i in range(len(template)):
        matched_tokens[template[i][0]] = defaultdict(int)
        
    with open(logfilepath, 'r') as lfin:
        for line in lfin:
            line = line.strip()
            message = outer_delimiter.join(line.split(outer_delimiter)[start:end])
            tokens = re.split(inner_delimiter, message)
            tokens = filter(lambda a: a != "", tokens)
            str_to_match = " ".join(tokens)
            for curr_tmp in template:
                id_template = curr_tmp[0]
                str_template = curr_tmp[1]
                cnt = str_template.count("(.*)")
                mch = re.match(str_template, str_to_match)
                if mch:
                    matched_count[id_template] += 1
                    for i in range(cnt):
                        matched_tokens[id_template][mch.group(i + 1)] += 1
                    break
    return matched_count, matched_tokens

def output_result(matched_count, matched_tokens, template, output_filepath):
    set_template = {}
    output_list = []
    for curr_tmp in template:
        set_template[curr_tmp[0]] = curr_tmp[1]
    for k,v in matched_count.iteritems():        
        meta_data = {}
        meta_data["id"] = k
        meta_data["count"] = v 
        meta_data["template"] = set_template[k]
        meta_data["tokens"] = matched_tokens[k]   
        output_list.append(meta_data)
    sorted_result = sorted(output_list, key = lambda x : x["id"])   
    output_json = json.dumps(sorted_result, sort_keys=True, indent=4, separators=(',', ': '))
    with open(output_filepath, 'w') as fout:
        fout.write(output_json)
        
if __name__ == "__main__":
    templatepath, logfilepath, peelerpath = parse_args()
    
    print "Retrieve message peeler."
    peeler = get_peeler(peelerpath)
    
    print "Load log templates."
    template = load_template(templatepath)
    
    print "Match log to templates."
    matched_count, matched_tokens = match_template(logfilepath, peeler, template)
    
    output_filepath = logfilepath + "_match_results"
    print "Write output to file " + output_filepath + "."
    output_result(matched_count, matched_tokens, template, output_filepath)
    print "Done."