import os
import json
import time
import collections
import subprocess

dist_docker_path = os.path.abspath(__file__).split('/')[:-1]
dist_docker_path = '/'.join(dist_docker_path) + '/'
# It requires servers.json
with open(os.path.join(dist_docker_path,'info.json')) as json_file:
  json_data = json.load(json_file)

master = json_data['master']
workers = json_data['workers']

def init_worker_info():

  if os.path.exists(os.path.join(dist_docker_path,'init_worker_info.json')):
    with open(os.path.join(dist_docker_path,'init_worker_info.json')) as json_file:
      sum_workers = json.load(json_file)
    return sum_workers

  #############################################################################
  # Workers
  #############################################################################
  sum_workers = []
  for i in range(len(workers)):
    _sum_workers = dict()
    _sum_workers['user'] = workers[i]['user']
    _sum_workers['host'] = workers[i]['host']

    # CPU
    _sum_workers['cpu'] = dict()
    output = subprocess.check_output(
      'ssh '+workers[i]['user']+'@'+workers[i]['host']+
        ' cat /sys/fs/cgroup/cpuset/cpuset.cpus',
      shell=True).decode('utf-8')
    _min, _max = output.split('\n')[0].split('-')
    cpu_usage = [0]*(int(_max)+1)
    _sum_workers['cpu']['total_num'] = len(cpu_usage)
    _sum_workers['cpu']['used_num'] = len(cpu_usage) - cpu_usage.count(0)
    _sum_workers['cpu']['cpu_usage'] = cpu_usage

    # Memory
    _sum_workers['memory'] = dict()
    output = subprocess.check_output(
      'ssh '+workers[i]['user']+'@'+workers[i]['host']+
        ' cat /proc/meminfo |grep MemTotal',
      shell=True).decode('utf-8')
    mem_kb = int(output.split('\n')[0].split(':')[1].split('k')[0])
    mem_gb = mem_kb // 1024 // 1024
    _sum_workers['memory']['total_size'] = mem_gb
    _sum_workers['memory']['used_size'] = 0

    # GPU
    _sum_workers['gpu'] = dict()
    try:
      output = subprocess.check_output(
        'ssh '+workers[i]['user']+'@'+workers[i]['host']+' nvidia-smi -L',
        shell=True).decode('utf-8')
      output = output.split('\n')[:-1]
      gpu_models = []
      for _output in output:
        gpu_info, UUID = _output.split('(')
        gpu_idx, gpu_model = gpu_info.split(':')
        gpu_models.append(gpu_model[1:-1])

      _sum_workers['gpu']['total_num'] = len(gpu_models)
      _sum_workers['gpu']['models'] = gpu_models
      _sum_workers['gpu']['gpu_usage'] = [0]*len(gpu_models)
    except:
      _sum_workers['gpu']['total_num'] = 0
      _sum_workers['gpu']['models'] = []
      _sum_workers['gpu']['gpu_usage'] = []

    sum_workers.append(_sum_workers)

  with open(os.path.join(dist_docker_path,'init_worker_info.json'), 'w') as outfile:
    json.dump(sum_workers, outfile)

  return sum_workers

def port_pretty(port_binding):
  res_str = ''
  for key in port_binding.keys():
    _res_str = []
    for i in range(len(port_binding[key])):
      _res_str.append(port_binding[key][i]['HostIp']+':'+port_binding[key][i]['HostPort'])
    _res_str = ','.join(_res_str)
    res_str += _res_str+'->'+key

    res_str +=','

  return res_str[:-1]

def count_duplicated(list_data):
  dict_data = collections.Counter(list_data)
  res_list = []
  for key in dict_data.keys():
    res_list.append(str(dict_data[key])+' '+key)

  return ','.join(res_list)

def summary():

  # init worker infos
  sum_workers = init_worker_info()

  #############################################################################
  # Containers
  #############################################################################
  sum_containers = []
  for i in range(len(sum_workers)):
    output = subprocess.check_output(
      'ssh '+workers[i]['user']+'@'+workers[i]['host']+
        " docker ps -a --format '{{.Names}}'",
      shell=True).decode('utf-8')
    output = output.split('\n')[:-1]

    for _output in output:
      _sum_containers = dict()
      details = subprocess.check_output(
        'ssh '+workers[i]['user']+'@'+workers[i]['host']+
          " docker inspect "+_output,
        shell=True).decode('utf-8')
      details = json.loads(details)[0]

      # Details
      _sum_containers['user'] = workers[i]['user']
      _sum_containers['host'] = workers[i]['host']
      _sum_containers['name'] = details['Name'][1:]
      _sum_containers['image'] = details['Config']['Image']
      _sum_containers['running'] = details['State']['Running']
      _sum_containers['created'] = details['Created'].split('.')[0][2:]
      port_binding = details['NetworkSettings']['Ports']
      _sum_containers['ports'] = port_pretty(port_binding)
      
      # CPU
      cpuset_cpus = details['HostConfig']['CpusetCpus'].split(',')
      cpuset_cpus = list(map(int, cpuset_cpus))
      _sum_containers['CPUS'] = len(cpuset_cpus)
      for cpu_idx in cpuset_cpus:
        sum_workers[i]['cpu']['cpu_usage'][cpu_idx] = _output
      sum_workers[i]['cpu']['used_num'] += len(cpuset_cpus)

      # Memory
      mem_gb = int(details['HostConfig']['Memory'])//1024//1024//1024
      _sum_containers['Mem'] = str(mem_gb)+'g'
      sum_workers[i]['memory']['used_size'] += mem_gb

      # GPU
      if details['Config']['Env'][0].split('=')[0] == 'NVIDIA_VISIBLE_DEVICES':
        gpus = details['Config']['Env'][0].split('=')[1].split(',')
        gpus = list(map(int, gpus))
        gpu_models = []
        for _gpu in gpus:
          gpu_models.append(sum_workers[i]['gpu']['models'][_gpu])
          sum_workers[i]['gpu']['gpu_usage'][_gpu] = _output
        _sum_containers['GPUS'] = count_duplicated(gpu_models)
      else:
        _sum_containers['GPUS'] = ''

      sum_containers.append(_sum_containers)

  return sum_workers, sum_containers

if __name__ == "__main__":

  sum_workers, sum_containers = summary()

  print(json.dumps(sum_workers, sort_keys=True, indent=2))
  print(json.dumps(sum_containers, sort_keys=True, indent=2))
