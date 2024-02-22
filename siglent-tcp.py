#!/usr/bin/env python3.7
# -*- coding: utf8 -*-

import vxi11
import numpy as np
import matplotlib.pyplot as plt
import argparse
import time
import datetime
import os

parser=argparse.ArgumentParser()
parser.add_argument('nwav', help='number of captures',type=int)
args=parser.parse_args()
nwav=args.nwav

home=os.environ['HOME']
dir='{0}/'.format(home)
date0=time.strftime('%y%m%d')
name='{0}{1}.dat1'.format(dir,date0)

if os.path.exists(name) == False:
  fdat=open(name,'w')
else:
  while os.path.exists(name) == True:
    fix=str(int(name[-1])+1)
    name=name[:-1]+fix
  fdat=open(name,'w')

wavenum=0
buffer_size=1024*1024*20

#ip address cofigured on scope
scope=vxi11.Instrument('10.11.13.220')
scope.write(':chdr off')

vthr=float(scope.ask(':c1:trlv?')) # threshold level mV
Tsam=scope.ask(':sara?')
units={'G':1e9,'M':1e6,'k':1e3}
for ut in units.keys():
  if Tsam.find(ut)!=-1:
    Tsam=Tsam.split(ut)
    Tsam=float(Tsam[0])*units[ut]
  break
Tsam=float(Tsam)
tdiv=float(scope.ask(':tdiv?'))
yfac=float(scope.ask(':c1:vdiv?'))
yoff=float(scope.ask(':c1:ofst?'))

print(yfac,yoff)

t0=time.time()
fecha=time.strftime('%d-%m-%y %H:%M:%S',time.localtime(t0))
fdat.write('RC {0}\n'.format(fecha))
fdat.write('TP: {0} {1} {2}\n'.format(vthr,tdiv,Tsam))
scope.write(':trmd single')

T=0
while (wavenum<nwav):
  while T!=1:
    q=int(scope.ask(':inr?'))
    k=int(scope.ask(':inr?'))
    T=0x00FF&q
    time.sleep(0.1)
  scope.write(':c1:wf? dat2')
  data=list(scope.read_raw()[15:])
  data.pop()
  data.pop()
  dlen=0
  volts=[]
  for d in data:
    if d>127:
      d=d-255
    else:
      pass
    volts.append(d)
  N=len(volts)
  if N==281:
    y=yfac*(np.array(volts)/25)-yoff
    if np.any(y[1:]<=vthr):
      ttrg=time.strftime('%H:%M:%S',time.localtime(time.time()))
      fdat.write('FC: {0} {1}\n'.format(ttrg,wavenum))
      np.savetxt(fdat,y,fmt='%1.4f',newline=' ')
      fdat.write('\n')
      wavenum+=1
  scope.write(':trmd single')

t1=time.time()
dt=datetime.timedelta(seconds=(t1-t0))
print(dt)
print('Acquisition completed in: {0} hrs'.format(str(dt)[0:7]))
print('Capture rate: {0} (Hz)'.format(nwav/dt.total_seconds()))
scope.close()
