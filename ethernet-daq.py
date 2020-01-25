#!/usr/bin/env python3.7
# -*- coding: utf8 -*-

import vxi11
import numpy as np
import argparse
import time
import datetime
import os

parser=argparse.ArgumentParser()
parser.add_argument('nwav', help='numero de capturas',type=int)
args=parser.parse_args()
nwav=args.nwav

home=os.environ['HOME']
ruta='{0}/proyectos/scicrt/scibar-fitting/sphe-response/'.format(home)
fecha=time.strftime('%y%m%d')
name='{0}{1}.adc1'.format(ruta,fecha)

if os.path.exists(name) == False:
  fdat=open(name,'w')
else:
  while os.path.exists(name) == True:
    fix=str(int(name[-1])+1)
    name=name[:-1]+fix
  fdat=open(name,'w')


wavenum=0
buffer_size=1024*1024*2
vth=-25.0e-3

scope=vxi11.Instrument("192.168.10.14")
scope.write(':*cls')
scope.write(':*cle')
scope.write(':head off')
scope.write(':verb off')
scope.write(':dat:sou ch1')
scope.write(':dat:enc fas')
scope.write(':wfmo:byt_n 1')
scope.write(':dis:wave off')

tdel=float(scope.ask(':hor:del:tim?'))
tpos=float(scope.ask(':hor:pos?'))
rlen=int(scope.ask(':hor:reco?'))
scope.write(':dat:star 1;stop {0}'.format(rlen))
Tsam=float(scope.ask(':wfmo:xin?'))
yfac=float(scope.ask(':wfmo:ymul?'))
yoff=float(scope.ask(':wfmo:yof?'))
scope.write(':curves?')

t0=time.time()
fecha=time.strftime('%d-%m-%y %H:%M:%S',time.localtime(t0))
fdat.write('RC {0}\n'.format(fecha))
fdat.write('TP: {0} {1} {2}\n'.format(tdel,tpos,Tsam))

while wavenum < nwav:
  bhead=''
  while(len(bhead)==0):
    bhead=scope.read(2)
    if (bhead==';\n'):
      bhead=''
  nbyte_count=int(bhead.replace('#',''))
  dlen=int(scope.read(nbyte_count))
  while dlen>0:
    if (dlen>=buffer_size):
      data=scope.read_raw(buffer_size)
      dlen-=buffer_size
    else:
      data=scope.read_raw(dlen+1)
      dlen=0
  data_int=np.fromstring(data[:-1],dtype=np.int8)
  y=yfac*(data_int-yoff)
  if np.any(y<vth):
    ttrg=time.strftime('%H:%M:%S',time.localtime(time.time()))
    fdat.write('FC: {0} {1}\n'.format(ttrg,wavenum))
    np.savetxt(fdat,y,fmt='%1.4f',newline=' ')
    fdat.write('\n')
    wavenum+=1


t1=time.time()
dt=datetime.timedelta(seconds=(t1-t0))
print(u'Adquisición completa en: {0} hrs.'.format(str(dt))[0:7])
print(u'Tasa de cuentas: {0} (Hz)'.format(nwav/dt.total_seconds()))
scope.write(':clear')
scope.write(':dis:wave on')
scope.close()
