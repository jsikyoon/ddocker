import os
import json
import subprocess

dist_docker_path = os.path.abspath(__file__).split('/')[:-1]
dist_docker_path = '/'.join(dist_docker_path) + '/'
# It requires servers.json
with open(os.path.join(dist_docker_path,'info.json')) as json_file:
  json_data = json.load(json_file)

master = json_data['master']
workers = json_data['workers']

print('Master: ',master)

###############################################################################
# Copy public keys
###############################################################################
for i in range(len(workers)):
  print(str(i)+'th Worker: ',workers[i])
  os.system('ssh-copy-id '+workers[i]['user']+'@'+workers[i]['host'])

###############################################################################
# Summarize docker images
###############################################################################
img_names = []
for i in range(len(workers)):
  repository = subprocess.check_output(
    'ssh '+workers[i]['user']+'@'+workers[i]['host']+" docker images --format '{{.Repository}}'",
    shell=True).decode('utf-8')
  repository = repository.split('\n')[:-1]
  tag = subprocess.check_output(
    'ssh '+workers[i]['user']+'@'+workers[i]['host']+" docker images --format '{{.Tag}}'",
    shell=True).decode('utf-8')
  tag = tag.split('\n')[:-1]

  for j in range(len(repository)):
    _img_name = repository[j]+':'+tag[j]
    if not _img_name in img_names:
      img_names.append(_img_name)
    else:
      print('Image name '+str(_img_name)+' is used twice. Please delete one of them.')
      exit(1)
    if workers[i]['host'] != master['host']:
      file_name = workers[i]['host']+'_'+str(j)+'_imgs'
      os.system('ssh '+workers[i]['user']+'@'+workers[i]['host']+
        ' docker save -o /tmp/'+file_name+' '+_img_name)
      os.system('scp '+workers[i]['user']+'@'+workers[i]['host']+
        ':/tmp/'+file_name+' '+'/tmp/')
      os.system('docker load -i /tmp/'+file_name)

# NOTE: Remove every container before starting
cont_names = []
for i in range(len(workers)):
    output = subprocess.check_output(
      'ssh '+workers[i]['user']+'@'+workers[i]['host']+" docker ps -a --format '{{.Names}}'",
      shell=True).decode('utf-8')
    output = output.split('\n')[:-1]
    if len(output) > 0:
      print('Please remove entire containers before starting.')
      exit(1)

print('Setting is Done!!')
