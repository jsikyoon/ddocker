# Distributed Docker (ddocker)

To manage multiple machines docker, we implemented simple and light-weight version of distributed docker. 

It supports commited image sharing between machines and creates container on a machine having available resource.

## Pre-requisites
- Install nvidia-docker on every machine.
- Install netstat on every machine to search available port number for allocation to containers.
## Installation
- git clone this repository.
- Write ```info.json``` based on ```info_template.json```
    - master and workers information
    - instance type that want to use
        - The type value format is ```[cpu num, memory size(GB), 'gpu_model1,gpu_model2']```
    - The number of CPU and memory size in ```buffer``` are not used anytime.
    - Port number is allocated from ```start_port_num```.
    - Additional options to create container can be added in ```additional_options``` like shared volumn.
```
{
  "master":{"host":,"user":},

  "workers":[
    {"host":,"user":},
    {"host":,"user":}
  ],

  "type":{
    "12 CPUS, 64 GB": [12, 64, ""],
    "12 CPUS, 64 GB, 1 TITAN XP": [12, 64, "TITAN Xp"],
    "24 CPUS, 128 GB, 2 TITAN XP": [24, 128, "TITAN Xp,TITAN Xp"],
  },

  "buffer":{
    "cpu": 5,
    "mem": 10
  },

  "start_port_num": 25000,

  "additional_options":[
    "-v /home/jsikyoon:/home/jsikyoon"
  ]
}
```
- Install by ``` python setup.py ```
    - ```setup.py``` does
        - Sharing public keys
        - Merging the images on master
            - It requires that every image name is distinct.
        - Checking containers
            - Every container need to be removed before starting.
- Add the installed location to PATH 
```export PATH=<ddocker_LOCATION>:$PATH```
```export DIST_DOCKER_PATH=<ddocker_LOCATION>```
- If you are user, please ask administrator to share authorized_keys to connect other machines.
- If you want to usr ddocker on other machines including master or one of workers, please do
    - Git clone this repository
    - Copy info.json from where you installed
    - Copy authorized_keys to connect
    - Add the location to PATH 
    ```export PATH=<ddocker_LOCATION>:$PATH```
```export DIST_DOCKER_PATH=<ddocker_LOCATION>```

## Commands
- It doesn't cover every command of docker, but we tried out to implement the useful commands for ML developments.
```
$ddocker --help

Usage: ddocker COMMAND [ARGUMENTS]

Commands:
  ddocker ps                                      List-up running containers
  ddocker ps [-a,--all]                           List-up every container
  ddocker images                                  List-up images
  ddocker inspect <CONTAINER_NAME>                Container details
  ddocker exec <CONTAINER_NAME>                   Access in container
  ddocker start <CONTAINER_NAME>                  Start container
  ddocker stop <CONTAINER_NAME>                   Stop container
  ddocker rm <CONTAINER_NAME>                     Remove container
  ddocker rmi <IMAGE_NAME>                        Remove image
  ddocker nvidia-smi <HOST_NAME>                  Show GPU usage
  ddocker create                                  Create/start container with selected types
  ddocker commit <CONTAINER_NAME> <IMAGE_NAME>    Commit container
  ```
  
  - Almost commands on above list work similar to docker, but ```create``` makes container by searching not used resources on the cluster. Bellowed is an example.
```
$ddocker create
Service types.
0 : 12 CPUS, 64 GB
1 : 12 CPUS, 64 GB, 1 TITAN XP
2 : 24 CPUS, 128 GB, 1 TITAN XP
3 : 24 CPUS, 128 GB, 2 TITAN XP
Select one of types (default: 0): 
Input the number of ports (default: 1): 
Docker Images.
0 : ubuntu:latest
1 : python3_cuda:latest
2 : nvidia/cuda:10.2-base
Select one of types (default: 0): 1
Input Container name (default: jsikyoon_20200530-003533): abc
Start to create
abc
Successfully created!
```

- ```ddocker ps -a``` example
```
$ddocker ps -a
NAME   PORT                       IMAGE                 CREATED             HOST        TYPE              RUNNING   
abc    0.0.0.0:25000->25000/tcp   python3_cuda:latest   20-05-29T15:35:39   jsik-server 12 cpus,64g mem   True
```

## Contact
Any feedback is welcome! If you have an issue, please don't hesitate to make issue on this repository.
