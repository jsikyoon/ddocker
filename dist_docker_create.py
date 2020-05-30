import os
import json
import random
import argparse
import subprocess
from datetime import datetime
from dist_utils import summary

def search_servers(sum_workers, type_info, buffers):
  num_cpu, mem_size, gpu_models = type_info
  if gpu_models == '':
    gpu_models = []
  else:
    gpu_models = gpu_models.split(',')
  cpu_buffer = buffers['cpu']
  mem_buffer = buffers['mem']
  
  # Check availability
  for i in range(len(sum_workers)):
    ava_num_cpu = \
      sum_workers[i]['cpu']['total_num'] \
      - sum_workers[i]['cpu']['used_num'] - cpu_buffer

    ava_mem_size = \
      sum_workers[i]['memory']['total_size'] \
      - sum_workers[i]['memory']['used_size'] - mem_buffer

    ava_gpu_models = []
    ava_gpu_idx_list = []
    for j in range(sum_workers[i]['gpu']['total_num']):
      if sum_workers[i]['gpu']['gpu_usage'][j] == 0:
        ava_gpu_models.append(sum_workers[i]['gpu']['models'][j])
        ava_gpu_idx_list.append(j)

    if ava_num_cpu < num_cpu:
      allocation = False
      continue

    if ava_mem_size < mem_size:
      allocation = False
      continue

    ava_gpu_flags = [0] * len(ava_gpu_models)
    for j in range(len(gpu_models)):
      for k in range(len(ava_gpu_models)):
        if gpu_models[j] == ava_gpu_models[k]:
          if ava_gpu_flags[k] == 0:
            ava_gpu_flags[k] = 1
            break
    if sum(ava_gpu_flags) < len(gpu_models):
      allocation = False
      continue

    # Pass every test
    user = sum_workers[i]['user']
    host = sum_workers[i]['host']

    cpuset_cpus = []
    for j in range(sum_workers[i]['cpu']['total_num']):
      if sum_workers[i]['cpu']['cpu_usage'][j] == 0:
        cpuset_cpus.append(str(j))
      if len(cpuset_cpus) == num_cpu:
        break
    cpuset_cpus = ','.join(cpuset_cpus)

    mem = str(mem_size)+'g'

    gpu_ids = []
    for j in range(len(ava_gpu_flags)):
      if ava_gpu_flags[j] == 1:
        gpu_ids.append(str(ava_gpu_idx_list[j]))
    gpu_ids = ','.join(gpu_ids)

    allocation = True
    break

  if allocation:
    return allocation, (user, host, cpuset_cpus, mem, gpu_ids)
  else:
    return allocation, None

def search_ports(num_port, start_port, cont_details):
  user = cont_details[0]
  host = cont_details[1]

  if num_port == 0:
    return ''

  port_nums = []
  _port_num = start_port
  for i in range(num_port):
    while True:
      try:
        if user == 'root':
          res = subprocess.check_output(
            'ssh '+user+'@'+host+
              " netstat -anp |grep ':"+str(_port_num)+" '",
            shell=True).decode('utf-8')
        else:
          res = subprocess.check_output(
            'ssh '+user+'@'+host+
              " sudo netstat -anp |grep ':"+str(_port_num)+" '",
            shell=True).decode('utf-8')
        _port_num += 1
      except:
        port_nums.append(_port_num)
        _port_num += 1
        break

  res = ''
  for _port_nums in port_nums:
    res += '-p '+str(_port_nums)+':'+str(_port_nums)+' '

  return res
    
def get_img_list(user, host):

  repo_list = subprocess.check_output(
    'ssh '+user+'@'+host+
      " docker images --format '{{.Repository}}'",
    shell=True).decode('utf-8')
  repo_list = repo_list.split('\n')[:-1]

  tag_list = subprocess.check_output(
    'ssh '+user+'@'+host+
      " docker images --format '{{.Tag}}'",
    shell=True).decode('utf-8')
  tag_list = tag_list.split('\n')[:-1]

  img_list = []
  for _repo, _tag in zip(repo_list, tag_list):
    img_list.append(_repo + ':' + _tag)

  return img_list

def sync_image(img_name, cont_details, master):
  user = cont_details[0]
  host = cont_details[1]
  img_list = get_img_list(user, host)

  # Check image is in target machine or not.
  flag = 0
  for _img in img_list:
    if _img == img_name:
      flag = 1
      break

  # Need to copy image to target machine.
  if flag == 0:
    file_name = str(random.randrange(1000000))+'_img'
    os.system('ssh '+master['user']+'@'+master['host']+
      ' docker save -o /tmp/'+file_name+' '+img_name)
    os.system('scp '+master['user']+'@'+master['host']+
      ':/tmp/'+file_name+' '+user+'@'+host+':/tmp/')
    os.system('ssh '+user+'@'+host+' docker load -i /tmp/'+file_name)

if __name__ == "__main__":
  dist_docker_path = os.path.abspath(__file__).split('/')[:-1]
  dist_docker_path = '/'.join(dist_docker_path) + '/'
  # It requires servers.json
  with open(os.path.join(dist_docker_path,'info.json')) as json_file:
    json_data = json.load(json_file)
  master = json_data['master']
  workers = json_data['workers']

  sum_workers, sum_conts = summary()

  #############################################################################
  # Select Type
  #############################################################################
  print('Service types.')
  idx = 0
  key_list = list(json_data['type'].keys())
  for key in key_list:
    print(idx,': '+key)
    idx += 1
  while True:
    sel_idx = input("Select one of types (default: 0): ")
    if sel_idx == '':
      sel_idx = '0'
    try:
      allocation, cont_details = search_servers(sum_workers,
                     json_data['type'][key_list[int(sel_idx)]],
                     json_data['buffer']
      )
      if not allocation:
        print('The selected option is not available. Please choose other type.')
      else:
        break
    except:
      print('Please input one of above options.')

  #############################################################################
  # Select the number of ports
  #############################################################################
  while True:
    num_port = input("Input the number of ports (default: 1): ")
    if num_port == '':
      num_port = '1'
    try:
      num_port = int(num_port)
      break
    except:
      print('Please input integer.')
  port_details = search_ports(num_port, json_data['start_port_num'], cont_details)

  #############################################################################
  # Select Image
  #############################################################################
  master_img_list = get_img_list(master['user'], master['host'])
  print('Docker Images.')
  idx = 0
  for _img in master_img_list:
    print(idx,': '+_img)
    idx += 1
  while True:
    sel_idx = input("Select one of types (default: 0): ")
    if sel_idx == '':
      sel_idx = '0'
    try:
      img_name = master_img_list[int(sel_idx)]
      break
    except:
      print('Please input one of above options.')

  #############################################################################
  # Make Container Name
  #############################################################################
  def_name = os.environ['USER']+'_'+datetime.now().strftime("%Y%m%d-%H%M%S")
  while True:
    cont_name = input("Input Container name (default: "+def_name+"): ")
    if cont_name == '':
      cont_name = def_name
    flag = 0
    for i in range(len(sum_conts)):
      if sum_conts[i]['name'] == cont_name:
        flag = 1
    if flag == 1:
      print('The Container Name '+cont_name+' exists. Please Input another.')
    else:
      break

  #############################################################################
  # Create and Run
  #############################################################################
  print('Start to create')
  sync_image(img_name, cont_details, master)
  user, host, cpuset_cpus, mem, gpu_ids = cont_details
  # Make Command
  command = ''
  command += 'ssh '+user+'@'+host+' '
  command += 'docker create '
  for _additional_option in json_data['additional_options']:
    command += _additional_option+' '
  command += port_details
  if gpu_ids != '':
    command += \
      '--device=/dev/nvidiactl --device=/dev/nvidia-uvm --device=/dev/nvidia'+\
      gpu_ids[0]+' -e NVIDIA_VISIBLE_DEVICES='+gpu_ids+' --runtime nvidia '
  command += '--memory='+mem+' '
  command += '--cpuset-cpus='+cpuset_cpus+' '
  command += '-ti --name '+cont_name+' '
  command += img_name+' /bin/bash'
  os.system(command)

  # Run container
  command = ''
  command += 'ssh '+user+'@'+host+' '
  command += 'docker start '+cont_name
  os.system(command)
  print('Successfully created!')
