#!/bin/bash

bench_name=""
result="res_"+$bench_name+".txt"
error="err_"$bench_name+".txt"



#SBATCH --job-name=$bench_name
#SBATCH --output=/data/scratch/sapients/hotspottuner/x10/src/$result
#SBATCH --error=/data/scratch/sapients/hotspottuner/x10/src/$error
#SBATCH -N 1
#SBATCH --time=24:00:00
#SBATCH --export=JAVA_HOME=/usr

cd /data/scratch/sapients/hotspottuner/x10/src/
scontrol show hostname $SLURM_JOB_NODELIST > /data/scratch/sapients/hotspottuner/x10/src/hosts.txt
export X10_HOSTFILE=/data/scratch/sapients/hotspottuner/x10/src/hosts.txt

#####!!! NOTE: You need to change this command accordingly to the benchmark you need to tune. 

/data/scratch/sapients/hotspottuner/x10/src/pythonenv/bin/python x10_managed_exe_tuner.py --path='/data/scratch/sapients/hotspottuner/x10/src/x10-benchmarks-2.5.2/KMEANS/' --source=kmeans --np=32 --main=KMeans --other='-n 320000 -c 4096 -d 12 -i 1' --flags=gc,compiler,compilation
