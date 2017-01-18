echo 'avrora started'
timeout 10s java -jar dacapo-9.12-bach.jar avrora
echo 'avrora killed'
sleep 5
echo 'eclipse started'
timeout 10s java -jar dacapo-9.12-bach.jar eclipse
echo 'eclipse killed'
sleep 5
echo 'fop started'
timeout 10s java -jar dacapo-9.12-bach.jar fop
echo 'fop killed'
sleep 5
