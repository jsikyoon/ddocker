import os
import subprocess
from datetime import datetime

###############################################################################
# Resource Option
###############################################################################
resource_options = {
        '8 CPU 50 GB': ['8', '50g'],
        '16 CPU 100 GB': ['16', '100g'],
}

for idx, key in enumerate(resource_options.keys()):
    print(idx,': '+key)

sel_idx = input("Select one of types (default: 0): ")
if sel_idx == '':
    sel_idx = '0'
sel_idx = int(sel_idx)

cpus, mem = resource_options[list(resource_options.keys())[sel_idx]]

os.system('gpustat -cpu')
gpu_ids = input("Select gpu indices (default: 0): ")
if gpu_ids == '':
    gpu_ids = '0'

###############################################################################
# Volumn options
###############################################################################
volumn_options="-v /data/local/jy651/:/data/local/jy651 -v /cortex/users/jy651:/cortex/users/jy651 "

###############################################################################
# Image Name
###############################################################################
repo_list = subprocess.check_output(" docker images --format '{{.Repository}}'",
        shell=True).decode('utf-8')
repo_list = repo_list.split('\n')[:-1]

tag_list = subprocess.check_output(" docker images --format '{{.Tag}}'",
        shell=True).decode('utf-8')
tag_list = tag_list.split('\n')[:-1]

img_list = []
for _repo, _tag in zip(repo_list, tag_list):
    img_list.append(_repo + ':' + _tag)

for idx, img_name in enumerate(img_list):
    print(idx,': '+img_name)

sel_idx = input("Select an image (default: 0): ")
if sel_idx == '':
    sel_idx = '0'
sel_idx = int(sel_idx)
img_name = img_list[sel_idx]

###############################################################################
# Container Name
###############################################################################
def_name = os.environ['USER']+'_'+datetime.now().strftime("%Y%m%d-%H%M%S")
cont_name = input("Input Container name (default: "+def_name+"): ")
if cont_name == '':
    cont_name = def_name

###############################################################################
# Create and Start
###############################################################################
command = 'docker create '
command += volumn_options
command += \
    '--device=/dev/nvidiactl --device=/dev/nvidia-uvm --runtime nvidia '
for _gpu_id in gpu_ids.split(','):
    command += '--device=/dev/nvidia'+_gpu_id+' '
command += '-e NVIDIA_VISIBLE_DEVICES='+gpu_ids+' '
command += '--memory='+mem+' '
command += '--cpus='+cpus+' '
command += '-ti --name '+cont_name+' '
command += img_name+' /bin/bash'
print(command)
os.system(command)

command = 'docker start '+cont_name
os.system(command)
