import argparse
import json
import re
import sys
from collections import defaultdict
from stopwords import stpwd, punct

def parse_args():
    argument_parse = argparse.ArgumentParser(description = "Clustering based log template miner.")
    argument_parse.add_argument("-s", action = "store", dest = "support", type = int, default = 50, help = "A positive number of support")
    argument_parse.add_argument("-f", action = "store", dest = "logfile", default = "./sample/access_log", help = "The log file to analyze")
    argument_parse.add_argument("-p", action = "store", dest = "peeler", default = "./peeler/access_log", help = "Log file's message peeler")
    results = argument_parse.parse_args()
    support = results.support
    logfilepath = results.logfile
    peelerpath = results.peeler
    return support, logfilepath, peelerpath

def get_peeler(peelerpath):
    with open(peelerpath, 'r') as pfin:
        line = pfin.readline()
        try:
            peeler = json.loads(line)
        except ValueError:
            print "--->Input file format error!"
            sys.exit(1)
    return peeler       

def build_vocabulary(logfilepath, peeler):
    vocabulary = defaultdict(int)
    outer_delimiter = peeler["outer_delimiter"]
    inner_delimiter = peeler["inner_delimiter"]
    start = int(peeler["message_start"])
    end = peeler["message_end"]
    if end != "":
        end = int(end)
    else:
        end = None
    with open(logfilepath, 'r') as fin:
        for line in fin:
            line = line.strip()
            message = outer_delimiter.join(line.split(outer_delimiter)[start:end])
            tokens = re.split(inner_delimiter, message)
            tokens = filter(lambda a: a != "", tokens)
            for i, token in enumerate(tokens):
                vocabulary[(token, i)] += 1
    return vocabulary

# Template length > 0 after all stop words and punctuation are filtered.
def evaluate_template(template):
    template_len = len(template)
    if template_len == 0:
        return False
    for curr_tuple in template:
        curr_word = curr_tuple[0]
    if curr_word in stpwd or curr_word in punct:
        if curr_word in punct:
            template_len -= 1
    if template_len > 0:
        return True
    else:
        return False

def transform_regex(template):
    place_holder = "YLPLACEHOLDER"
    temp_regex = []
    for curr_tem in template:
        curr_list = list(curr_tem)
        word_len = curr_list[-1][1] + 1
        temp_list = [None] * word_len
        all_slot_set = set(range(word_len))
        taken_slot = []
        for curr_token in curr_list:
            taken_slot.append(curr_token[1])
        taken_slot_set = set(taken_slot)
        empty_slot_set = all_slot_set - taken_slot_set
        temp_str = None
        if empty_slot_set:
            for i in empty_slot_set:
                temp_list[i] = place_holder
            for curr_token in curr_list:
                temp_list[curr_token[1]] = curr_token[0]
            temp_str = " ".join(temp_list)
        else:
            temp_list = [token[0] for token in curr_list]
            temp_str = " ".join(temp_list)
        regex_str = temp_str.replace(place_holder, "*")
        temp_regex.append(regex_str)
    sorted_temp_regex = sorted(temp_regex, key = lambda x : len(x), reverse = True)
    return sorted_temp_regex     
        
        
def build_template(logfilepath, vocabulary, support, peeler):
    voc_by_sup = {k:v for (k,v) in vocabulary.iteritems() if v >= support}
    outer_delimiter = peeler["outer_delimiter"]
    inner_delimiter = peeler["inner_delimiter"]
    start = int(peeler["message_start"])
    end = peeler["message_end"]
    if end != "":
        end = int(end)
    else:
        end = None
    with open(logfilepath, 'r') as fin:
        template = defaultdict(int)
        for line in fin:
            line = line.strip()
            message = outer_delimiter.join(line.split(outer_delimiter)[start:end])
            tokens = re.split(inner_delimiter, message)
            tokens = filter(lambda a: a != "", tokens)
            curr_list = []
            for i, token in enumerate(tokens):
                if (token, i) in voc_by_sup:
                    curr_list.append((token, i))
            if evaluate_template(curr_list):
                curr_tuple = tuple(curr_list)
                template[curr_tuple] += 1
    tem_by_sup = {k:v for (k,v) in template.iteritems() if v >= support}
    
    # Filter out short templates who are contained in others
    def not_contained(tem, all_tem):
        to_compare = set(tem)
        for curr_tem in all_tem:
            curr_set = set(curr_tem)           
            if to_compare.issubset(curr_set) and not curr_set.issubset(to_compare):
                return False
        return True
    tem_filtered = filter(lambda a: not_contained(a, tem_by_sup), tem_by_sup)
    
    return tem_filtered  

def output_template(outputpath, regex, support):
    output_list = []
    for i, v in enumerate(regex):
        temp_item = {}
        temp_id = str(support).zfill(5) + str(i).zfill(5)
        temp_item["id"] = temp_id
        temp_item["template"] = v 
        output_list.append(temp_item)
    output_json = json.dumps(output_list, sort_keys=True, indent=4, separators=(',', ': '))
    with open(outputpath, 'w') as fout:
        fout.write(output_json)

if __name__ == "__main__":
    support, logfilepath, peelerpath = parse_args()
    
    print "Retrieve message peeler."
    peeler = get_peeler(peelerpath)
    
    print "Build vocabulary."
    vocabulary = build_vocabulary(logfilepath, peeler)
     
    print "Summarize template."
    template = build_template(logfilepath, vocabulary, support, peeler)
     
    print "Convert to Regex."
    regex = transform_regex(template)
      
    output_filepath = logfilepath + "_template_" + str(support)
    print "Write templates to file " + output_filepath + "."
    output_template(output_filepath, regex, support)
    
    print "Done."
