
#!/bin/sh

USER_HOME=${HOME};


java $3 -cp ./*:$CLASSPATH:./lib/* debs2015.ManagerWithFileWriteThread_Handler_2  $1 $2
