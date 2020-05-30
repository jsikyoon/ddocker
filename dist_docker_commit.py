import os
import json
import argparse
from dist_utils import summary
from dist_docker_create import get_img_list

parser = argparse.ArgumentParser(description='Create image.')
parser.add_argument('--cont', type=str, default='aaa', help='the container name')
parser.add_argument('--new_img', type=str, default='aaa', help='the new name')

args = parser.parse_args()
cont_name = args.cont
new_img_name = args.new_img

dist_docker_path = os.path.abspath(__file__).split('/')[:-1]  
dist_docker_path = '/'.join(dist_docker_path) + '/'  
# It requires servers.json
with open(os.path.join(dist_docker_path,'info.json')) as json_file:
  json_data = json.load(json_file)
master = json_data['master']
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
  if not ':' in new_img_name:
    new_img_name += ':latest'
  img_list = get_img_list(master['user'], master['host'])
  if new_img_name in img_list:
    print('The Image name '+new_img_name+' exists.')
    exit(1)
  command = 'ssh '
  command += sum_conts[i]['user']+'@'+sum_conts[i]['host']
  command += ' docker commit ' + cont_name + ' '+new_img_name
  os.system(command)
  # Update master node image list
  if sum_conts[i]['host'] != master['host']:
    file_name = sum_conts[i]['host']+'_'+new_img_name+'_img'
    os.system('ssh '+sum_conts[i]['user']+'@'+sum_conts[i]['host']+
      ' docker save -o /tmp/'+file_name+' '+new_img_name)
    os.system('scp '+sum_conts[i]['user']+'@'+sum_conts[i]['host']+
      ':/tmp/'+file_name+' '+
      master['user']+'@'+master['host']+':/tmp/')
    os.system('ssh '+master['user']+'@'+master['host']+
              ' docker load -i /tmp/'+file_name)


