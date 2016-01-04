logminer
=======
A set of tools for log analytics, from data processing to advanced modeling. Tools are organized in folders with sample data to play with. Brief instructions are documented here. For Chinese description of this project, please check out my [blog](http://blog.csdn.net/cameling_yang).

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
###LogReduce

With [LogTemplate](https://github.com/cameling/logminer/tree/master/LogTemplate), one immediate interesting analytics we could do is to summarize high volume logs. You may heard about SumoLogic's [LogReduce](https://www.sumologic.com/2012/03/23/what-the-heck-is-logreduce/). The tool will do similar thing for you. Here's the usage:
```
$ python reduce.py -h
usage: reduce.py [-h] [-t TEMPLATEFILE] [-f LOGFILE] [-p PEELER]

Log summarization based on templates.

optional arguments:
  -h, --help       show this help message and exit
  -t TEMPLATEFILE  The template file
  -f LOGFILE       The log file to analyze
  -p PEELER        Log file's message peeler
```
* Templatefile is the output of [LogTemplate](https://github.com/cameling/logminer/tree/master/LogTemplate).
* Peeler is the same as defined in [LogTemplate](https://github.com/cameling/logminer/tree/master/LogTemplate). We need it here because we should do the summrization in the same way as we mine the template.

The exampled input log file and output summarizations are in the sample folder, using:
```
$ python reduce.py -t sample/access_log_template_50 -f sample/access_log -p peeler/access_log
```
###Utils
This project contains various small utilities to ease the use of LogMiner tool set.

####peeler_helper
Use this tool to quickly test the outer delimiter and find the start/end position of log message.
```
$ python peeler_helper.py -h
usage: peeler_helper.py [-h] [-o OUTER_DELIMITER] [-l LOG_LINE]

Log Peeler Helper.

optional arguments:
  -h, --help          show this help message and exit
  -o OUTER_DELIMITER  Outer delimiter as in the peeler file
  -l LOG_LINE         The sampled log line encapsulated by quotation marks
```
The script will print the tokens with its position split by the out delimiter, for example:
```
$ python peeler_helper.py -o " " -l "2015-12-22 07:54:51  [ qtp1081769770-22:171647 ] - [ INFO ]  Start to construct topology graph."
|0|:2015-12-22 |1|:07:54:51 |2|: |3|:[ |4|:qtp1081769770-22:171647 |5|:] |6|:- |7|:[ |8|:INFO |9|:] |10|: |11|:Start |12|:to |13|:construct |14|:topology |15|:graph.
```
In this case, the outer delimiter is a blank space (" "), the log message "Start to construct topology graph." starts from position 11.