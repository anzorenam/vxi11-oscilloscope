#!/usr/bin/env python3.9
# -*- coding: utf8 -*-

import matplotlib.pyplot as plt
import numpy as np

name='240215.dat18' # name of file
data=np.loadtxt(name,skiprows=1,comments='FC:')
N,M=np.shape(data[:,1:])  # N waveforms of lenght M each
                          # we throw the first byte of each waveform because is noise

ysca,tsca=1000.0,1e9 # to change scale of waveform to mV and ns
tdiv=0.0
Tsam=1e9
tds=-1.0*(14/2*tdiv)+(1.0/Tsam)*np.arange(int(M))
for j in range(0,N):
  fig,ax=plt.subplots(nrows=1,ncols=1,sharex=False,sharey=False)
  ax.plot(tsca*tds,ysca*data[j,1:])
  ax.set_xlabel('Time [ns]',x=0.9)
  ax.set_ylabel('Amplitude [mV]')
  plt.show()
