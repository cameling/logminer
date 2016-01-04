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