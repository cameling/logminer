###LogTemplate
The first step to do any analytics against semi-structured logs is getting **templates** to handle them. Templates could be in many forms. The most popular form is a regular expression. With templates, free-text log messages become structured and are easy to consumed by analytics algorithms.

This tool using clustering techniques to mine templates from history logs. Here's the usage:
```
$ python template.py -h
usage: template.py [-h] [-s SUPPORT] [-f LOGFILE] [-p PEELER]

Clustering based log template miner.

optional arguments:
  -h, --help  show this help message and exit
  -s SUPPORT  A positive number of support
  -f LOGFILE  The log file to analyze
  -p PEELER   Log file's message peeler
```
* Support is an integer value that tunes mined templates' quality. Higher value means more samples support the template, but you get less templates, vice versa. 
* Peeler is a simple configuration tells the tool where to to look at in a line of raw log, and how to analyze. 

For example, the sampled peeler is for a typical access log, to analyze visited URLs. It's a json in *one line* with four key-value pairs.
```
{"outer_delimiter":" ","inner_delimiter":" |/|\"","message_start":"5","message_end":"-2"}
```
* *outer_delimiter*, *message_start* and *message_end* locate the message you'd like to analyze. Delimiters are designated following the regular expression fashion. Usually a whitespace (" ") will do the trick. Start and end positions follow the Python list fashion. If the message's end position is EOF (End of Line), just use a blank string ("").
* *inner_delimiter* tells the tool how to analyze the message. In this case, as URL is delimited by "/" so we add it in.

The exampled input log file and output templates with support set to 50 are in the sample folder, using:
```
$ python template.py -s 50 -f sample/access_log -p peeler/access_log
```