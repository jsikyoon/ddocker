import os
import json
import argparse
from dist_utils import summary

parser = argparse.ArgumentParser(description='Create container.')
parser.add_argument('--cont', type=str, default='gvt', help='the container name')

args = parser.parse_args()
cont_name = args.cont

dist_docker_path = os.path.abspath(__file__).split('/')[:-1]
dist_docker_path = '/'.join(dist_docker_path) + '/'
# It requires servers.json
with open(os.path.join(dist_docker_path,'info.json')) as json_file:
  json_data = json.load(json_file)
sum_workers, sum_conts = summary()

flag = 0
for i in range(len(sum_conts)):
  if sum_conts[i]['name'] == cont_name:
    flag = 1
    break

if flag == 0:
  print('The Container '+cont_name+' is not existed.')
  exit(1)
else:
  command = 'ssh '
  command += sum_conts[i]['user']+'@'+sum_conts[i]['host']
  command += ' docker inspect ' + cont_name
  os.system(command)
