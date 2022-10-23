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
    command_cp_shap = 'cp ../feature_selection.py '+ path_now  # Linux
else:
    command_cp_shap = 'copy D:\\feature_selection\\workdir\\feature_selection.py '+ path_now  # Windows

os.system(command_cp_shap)

command = 'python feature_selection.py'
with open('log.txt', 'a') as fp:
    fp.write('running\n')

os.system(command)

if system_plat == "Linux":
    os.system('rm feature_selection.py')  # Linux
else:
    os.system('del feature_selection.py')  # Windows


with tarfile.open('./result.tar.gz', 'w:gz') as tar:
    for filename in os.listdir():
        if filename in ['result.xml', 'parameters.txt', 'log.txt', 'feature_selection_API.py']:
            continue
        tar.add(filename)