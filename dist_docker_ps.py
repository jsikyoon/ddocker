import os
import json
import argparse
import subprocess
from dist_utils import summary

parser = argparse.ArgumentParser(description='List containers')
parser.add_argument('-a', action='store_true', help='List-up all containers')

args = parser.parse_args()
all_flag = args.a

_, sum_conts = summary()

buffers = 3
# Header
header = ['NAME', 'PORT', 'IMAGE', 'CREATED', 'HOST', 'TYPE', 'RUNNING']

# To make pretty
len_col = []
for i in range(len(header)):
  len_col.append(len(header[i]))

key_list = ['name', 'ports', 'image', 'created', 'host', 'type', 'running']
vals = []
for i in range(len(sum_conts)):
  _vals = []
  for j in range(len(header)):

    if not all_flag:
      if not sum_conts[i]['running']:
        continue

    if key_list[j] == 'type':
      val = ''
      val += str(sum_conts[i]['CPUS'])+' cpus,'+\
             str(sum_conts[i]['Mem'])+' mem,'+\
             str(sum_conts[i]['GPUS'])
      _vals.append(val)
      len_val = len(val)
    else:
      val = str(sum_conts[i][key_list[j]])
      _vals.append(val)
      len_val = len(val)

    if len_col[j] < len_val:
      len_col[j] = len_val

  vals.append(_vals)

for i in range(len(len_col)):
  len_col[i] = str(len_col[i] + buffers)

# Write Header
for i in range(len(header)):
  print('{:{width}}'.format(header[i],width=len_col[i]), end='')
print()

# Contents
for i in range(len(sum_conts)):
  for j in range(len(header)):
    print('{:{width}}'.format(vals[i][j],width=len_col[j]), end='')
  print()
