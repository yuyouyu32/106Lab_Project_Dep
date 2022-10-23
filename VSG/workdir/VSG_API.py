import os
import sys
import tarfile


# Get task id
TID = sys.argv[1]
import platform
system_plat = platform.system()


# copy shap_func.py
path_now = os.getcwd()

if system_plat == "Linux":
    command_cp_shap = 'cp ../VSG.py '+ path_now  # Linux
else:
    command_cp_shap = 'copy D:\\VSG\\workdir\\VSG.py '+ path_now  # Windows
    

os.system(command_cp_shap)

command = 'python VSG.py'
with open('log.txt', 'a') as fp:
    fp.write('running\n')

os.system(command)

if system_plat == "Linux": 
    os.system('rm VSG.py')  # Linux
else:
    os.system('del VSG.py')  # Windows
    





with tarfile.open('./result.tar.gz', 'w:gz') as tar:
    for filename in os.listdir():
        if filename in ['result.xml', 'parameters.json', 'log.txt', 'VSG_API.py']:
            continue
        tar.add(filename)
