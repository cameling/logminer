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