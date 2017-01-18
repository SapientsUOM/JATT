echo 'SPECjvm2008 Startup Benchmark Sheduler. Each Tuner Will Run for 90 minutes before killed. Waits 10s in between each job.'
echo 'python jvmtuner.py --TunerType=spec_startup with all the flags..'

echo 'Tuning benchmark Name:startup.crypto.aes'
timeout 5400s python jvmtuner.py --TunerType=spec_startup --source=startup.crypto.aes
sleep 20

echo 'Tuning benchmark Name:startup.crypto.rsa'
timeout 5400s python jvmtuner.py --TunerType=spec_startup --source=startup.crypto.rsa
sleep 20


echo 'Tuning benchmark Name:startup.crypto.signverify'
timeout 5400s python jvmtuner.py --TunerType=spec_startup --source=startup.crypto.signverify
sleep 20

echo 'Tuning benchmark Name:startup.mpegaudio'
timeout 5400s python jvmtuner.py --TunerType=spec_startup --source=startup.mpegaudio
sleep 20

echo 'Tuning benchmark Name:startup.scimark.fft'
timeout 5400s python jvmtuner.py --TunerType=spec_startup --source=startup.scimark.fft
sleep 20

echo 'Tuning benchmark Name:startup.scimark.lu'
timeout 5400s python jvmtuner.py --TunerType=spec_startup --source=startup.scimark.lu 
sleep 20

echo 'Tuning benchmark Name:startup.scimark.sor'
timeout 5400s python jvmtuner.py --TunerType=spec_startup --source=startup.scimark.sor
sleep 20

echo 'Tuning benchmark Name:startup.scimark.sparse'
timeout 5400s python jvmtuner.py --TunerType=spec_startup --source=startup.scimark.sparse
sleep 20

echo 'Tuning benchmark Name:startup.serial'
timeout 5400s python jvmtuner.py --TunerType=spec_startup --source=startup.serial
sleep 10

echo 'Tuning benchmark Name:startup.sunflow'
timeout 5400s python jvmtuner.py --TunerType=spec_startup --source=startup.sunflow
sleep 10

echo 'Tuning benchmark Name:startup.xml.transform'
timeout 5400s python jvmtuner.py --TunerType=spec_startup --source=startup.xml.transform
sleep 10

echo 'Tuning benchmark Name:startup.xml.validation'
timeout 5400s python jvmtuner.py --TunerType=spec_startup --source=startup.xml.validation
sleep 10

echo 'Tuning benchmark Name:startup.scimark.monte_carlo'
timeout 5400s python jvmtuner.py --TunerType=spec_startup --source=startup.scimark.monte_carlo
sleep 10
