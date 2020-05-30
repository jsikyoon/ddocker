import os
import json
import argparse

parser = argparse.ArgumentParser(description='Check GPU Usage')
parser.add_argument('--host', type=str, default='aaa', help='the host name')

args = parser.parse_args()
host = args.host

dist_docker_path = os.path.abspath(__file__).split('/')[:-1]
dist_docker_path = '/'.join(dist_docker_path) + '/'
# It requires servers.json
with open(os.path.join(dist_docker_path,'info.json')) as json_file:
  json_data = json.load(json_file)

master = json_data['master']
workers = json_data['workers']

flag = 0
for i in range(len(workers)):
  if workers[i]['host'] == host:
    flag = 1
    break

if flag == 0:
  print('The host '+host+' is not existed.')
else:
  os.system('ssh '+workers[i]['user']+'@'+workers[i]['host']+' nvidia-smi')

