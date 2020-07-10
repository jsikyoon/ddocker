import os, sys
import subprocess
from datetime import datetime

cpus = sys.argv[1]
mem = sys.argv[2]
gpu_ids = sys.argv[3]
img_name = sys.argv[4]
cont_name = sys.argv[5]
env_name = sys.argv[6]
run_command = ' '.join(sys.argv[7:])

###############################################################################
# Volumn options
###############################################################################
volumn_options="-v /data/local/jy651/:/data/local/jy651 -v /cortex/users/jy651:/cortex/users/jy651 "

###############################################################################
# Run
###############################################################################
command = 'docker run '
command += volumn_options
command += \
    '--device=/dev/nvidiactl --device=/dev/nvidia-uvm --runtime nvidia '
for _gpu_id in gpu_ids.split(','):
    command += '--device=/dev/nvidia'+_gpu_id+' '
command += '-e NVIDIA_VISIBLE_DEVICES='+gpu_ids+' '
command += '--memory='+mem+' '
command += '--cpus='+cpus+' '
command += '-ti --name '+cont_name+' '
command += img_name
command += ' /bin/bash -c "source ~/.bashrc; eval $(conda shell.bash hook) ;'
command += ' conda activate '+env_name+' ; '
command += run_command+'"'
print(command)
os.system(command)
