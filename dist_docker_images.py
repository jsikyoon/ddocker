import os
import json

dist_docker_path = os.path.abspath(__file__).split('/')[:-1]
dist_docker_path = '/'.join(dist_docker_path) + '/'
# It requires servers.json
with open(os.path.join(dist_docker_path,'info.json')) as json_file:
  json_data = json.load(json_file)

master = json_data['master']
os.system('ssh '+master['user']+'@'+master['host']+' docker images')

