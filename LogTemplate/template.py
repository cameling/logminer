import argparse
import json
import re
import string
import sys
from collections import defaultdict
from LogTemplate.stopwords import words, punct

def parse_args():
    argument_parse = argparse.ArgumentParser(description = "Clustering based log template miner.")
    argument_parse.add_argument("-s", action = "store", dest = "support", type = int, help = "A positive number of support")
    argument_parse.add_argument("-p", action = "store", dest = "path", help = "Path to the log file")
    results = argument_parse.parse_args()
    support = results.support
    filepath = results.path
    return support, filepath

def build_vocabulary(filepath):
    vocabulary = defaultdict(int)
    with open(filepath, 'r') as fin:
        for line in fin:
            try:
                json_line = json.loads(line)
            except ValueError:
                print "--->Input file format error!"
                sys.exit(1)
            message = json_line["message"].strip()
            words = message.split()
            for i, word in enumerate(words):
                vocabulary[(word, i)] += 1
    eval_vocab = {k:v for (k,v) in vocabulary.iteritems() if evaluate_vocabulary(k)}
    return eval_vocab

# Template length > 0 after all stop words and punctuation are filtered.
def evaluate_template(template):
    template_len = len(template)
    if template_len == 0:
        return False
    for curr_tuple in template:
        curr_word = curr_tuple[0]
    if curr_word in words or curr_word in punct:
        if curr_word in punct:
            template_len -= 1
    if template_len > 0:
        return True
    else:
        return False

# Vocabulary contains not only numbers and punctuation
def evaluate_vocabulary(vocabulary):
    vocab_text = vocabulary[0]
    for i in vocab_text:
        if not (i.isdigit() or i in string.punctuation):
            return True
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
        regex_str = re.escape(temp_str)
        regex_str = regex_str.replace(place_holder, "(.*)")
        temp_regex.append(regex_str)
    sorted_temp_regex = sorted(temp_regex, key = lambda x : len(x), reverse = True)
    return sorted_temp_regex     
        
        
def build_template(filepath, vocabulary, support):
    voc_by_sup = {k:v for (k,v) in vocabulary.iteritems() if v >= support}
    with open(filepath, 'r') as fin:
        template = defaultdict(int)
        for line in fin:
            try:
                json_line = json.loads(line)
            except ValueError:
                print "--->Input file format error!"
                sys.exit(1)
            message = json_line["message"].strip()
            words = message.split()
            curr_list = []
            for i, word in enumerate(words):
                if (word, i) in voc_by_sup:
                    curr_list.append((word, i))
            if evaluate_template(curr_list):
                curr_tuple = tuple(curr_list)
                template[curr_tuple] += 1
    tem_by_sup = {k:v for (k,v) in template.iteritems() if v >= support}
    return tem_by_sup  

def output_template(filepath, regex, support):
    output_list = []
    for i, v in enumerate(regex):
        temp_item = {}
        temp_id = str(support).zfill(5) + str(i).zfill(5)
        temp_item["id"] = temp_id
        temp_item["template"] = v 
        output_list.append(temp_item)
    output_json = json.dumps(output_list, sort_keys=True, indent=4, separators=(',', ': '))
    with open(filepath, 'w') as fout:
        fout.write(output_json)

if __name__ == "__main__":
    support, filepath = parse_args()
    
    print "Build vocabulary."
    vocabulary = build_vocabulary(filepath)
    
    print "Summarize Template."
    template = build_template(filepath, vocabulary, support)
    
    print "Convert to Regex."
    regex = transform_regex(template)
     
    output_filepath = filepath + "_template_" + str(support)
    print "Write templates to file " + output_filepath + "."
    output_template(output_filepath, regex, support)
    print "Done."