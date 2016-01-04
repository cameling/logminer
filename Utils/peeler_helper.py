import argparse

def parse_arg():
    argument_parse = argparse.ArgumentParser(description = "Log Peeler Helper.")
    argument_parse.add_argument("-o", action = "store", dest = "outer_delimiter", help = "Outer delimiter as in the peeler file")
    argument_parse.add_argument("-l", action = "store", dest = "log_line", help = "The sampled log line encapsulated by quotation marks")
    results = argument_parse.parse_args()
    outer_delimiter = results.outer_delimiter
    log_line = results.log_line
    return outer_delimiter, log_line

if __name__ == "__main__":
    outer_delimiter, log_line = parse_arg()
    split_line = log_line.split(outer_delimiter)
    for i in range(len(split_line)):
        print "|" +str(i) + "|:" + split_line[i],