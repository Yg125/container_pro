import os
import docker


# 根据服务名找出容器运行在哪个服务器，再找出对应的容器 返回container对象
def findcontainer(service_name):
    result = os.popen('DOCKER_HOST=tcp://219.223.251.96:2375 docker service ps ' + service_name + ' | grep Running').read().split()
    if result[3] == 'micc-PowerEdge-R840':
        ip_address = '219.223.251.96'
        client = docker.DockerClient(base_url='tcp://219.223.251.96:2375')
        output = os.popen('DOCKER_HOST=tcp://219.223.251.96:2375 docker ps | grep ' + service_name).read().split()
    elif result[3] == 'micc-95':
        ip_address = '219.223.251.95'
        client = docker.DockerClient(base_url='tcp://219.223.251.95:2375')
        output = os.popen('DOCKER_HOST=tcp://219.223.251.95:2375 docker ps | grep ' + service_name).read().split()
    else:
        ip_address = '219.223.251.94'
        client = docker.DockerClient(base_url='tcp://219.223.251.94:2375')
        output = os.popen('DOCKER_HOST=tcp://219.223.251.94:2375 docker ps | grep ' + service_name).read().split()
    container = client.containers.get(container_id=output[0])
    return container, ip_address
