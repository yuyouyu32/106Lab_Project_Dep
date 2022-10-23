#!/bin/bash
mpifort -O2 var_global.f90 libsisso.f90 DI.f90 FC.f90 SISSO.f90 -o SISSO
cp SISSO /home/draght/SISSO_new/SISSO-master/input_template/SISSO
cd /home/draght/SISSO_new/SISSO-master/input_template/
./SISSO
