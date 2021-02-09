# UCSC hexmap data server

Install the viewer first at:
```
 https://github.com/stuartlab-UCSC/hexmap-view
```
The instructions for installing this server will be within that code at:
```
 $HEXMAP/docs/dev/installData.html#
```









## Start server
```
cd $HEXCALC
bin/start
```

## Check to see if the process is running
```
pgrep -U $HEX_UID uwsgi
```
You may confirm the server is accessible via HTTP by using this URL in a 
browser where DATA_SERVER is as defined in your config.sh.
```
DATA_SERVER/test
```
This URL should return
```
"just testing data server"
```

## Stop server
```
Check for the process with the lowest process ID running as above.
kill <process-ID>
```


