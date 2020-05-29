import os
import json
import argparse
from dist_utils import summary

parser = argparse.ArgumentParser(description='Create container.')
parser.add_argument('--img', type=str, default='aaa', help='the image name')

args = parser.parse_args()
img_name = args.img

dist_docker_path = os.environ['DIST_DOCKER_PATH']
# It requires servers.json
with open(os.path.join(dist_docker_path,'info.json')) as json_file:
  json_data = json.load(json_file)
master = json_data['master']

command = 'ssh '
command += master['user']+'@'+master['host']
command += ' docker rmi ' + img_name
os.system(command)
