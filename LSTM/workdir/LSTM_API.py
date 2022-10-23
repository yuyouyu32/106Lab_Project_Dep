import os
import sys
import tarfile

# Get task id
TID = sys.argv[1]
module_name = 'LSTM'

import platform

system_plat = platform.system()
# copy shap_func.py
path_now = os.getcwd()
if system_plat == "Linux":
    command_cp_shap = f'cp ../{module_name}.py '+ path_now  # Linux
else:
    command_cp_shap = f'copy D:\\{module_name}\\workdir\\{module_name}.py '+ path_now  # Windows

os.system(command_cp_shap)

command = f'python {module_name}.py'
with open('log.txt', 'a') as fp:
    fp.write('running\n')

os.system(command)
if system_plat == "Linux":
    os.system(f'rm {module_name}.py')  # Linux
else:
    os.system(f'del {module_name}.py')  # Windows


with tarfile.open('./result.tar.gz', 'w:gz') as tar:
    for filename in os.listdir():
        if filename in ['result.xml', 'parameters.json', 'log.txt', 'LSTM_API.py']:
            continue
        tar.add(filename)