#!/usr/bin/env python
# -*- coding: utf-8 -*-

## Author: Peter Nadrah
## License: GNU GPL v3
## Description: Part of WLIC - simple GUI program for collecting spectra from
##              spectrometer.

import seabreeze
from seabreeze.spectrometers import list_devices, Spectrometer
import numpy as np

### SPECTROMETER COMMUNICATION ###
MAX_COUNTS = 2**16
MAX_INTENSITY = MAX_COUNTS * 0.85

class SpComm:
  _sp = None
  wavelengths = []
  
  def connectToDevice(self):
    devices = list_devices()
    if len(devices) == 0:
      return False
    
    self._sp = Spectrometer.from_first_available()
    self.calculateWavelengths()
    return True

  def calculateWavelengths(self):
    # USB2000+ coeficients for wavelength calculation
    intercept = 177.40000
    coef1 = 3.80800E-1
    coef2 = -1.40759E-5
    coef3 = -2.36589E-9
    self.wavelengths = list(map(lambda x: intercept + coef1*x + coef2*x**2 + coef3*x**3, range(0, 2048)))

  # testing
  def optimizeIntegrationTime(self):
    tStart = 1000 # usec
    tEnd = 1000000
    tStep = 1000
    tOptimal = tStart
    """
    tRange = [t for t in range(1, 10, 1)]
    tRange.extend([t for t in range(1*10, 10*10, 1*10)])
    tRange.extend([t for t in range(1*100, 11*100, 1*100)])
    """
    tRange = [t for t in range(1, 6, 1)]
    t = 6.0
    while t <= 1000:
      tRange.append(round(t))
      t = round(t)*1.2
    print (tRange)
    
    for t in tRange:
      self.setIntegrationTime(t*1000)
      sp = self.readSpectrumFromDevice(1)
      if np.amax(sp['ys']) > MAX_INTENSITY:
        # choose the last int. time and break
        break
      tOptimal = t * 1000
    
    print ('tOptimal', tOptimal)
    return tOptimal

  def setIntegrationTime(self, integrationTime):
    self._sp.integration_time_micros(integrationTime)

  def readSpectrumFromDevice(self, scansToAverage=1, boxcarWidth=0, correctDarkCounts=False, correctNonlinearity=False, callback=None):
    # for testing:
    #return readSpectrumFromFile(os.path.join(dir, '5_uv-vis/counts.txt'))
    #return {'xs': np.linspace(180., 800., num=2048), 'ys': np.random.default_rng().integers(low=500, high=50000, size=2048)}
    #return {'ys': np.random.default_rng().integers(low=500, high=50000, size=2048)}
    
    if self._sp == {}:
      return {}
    
    # get wavelengths
    #wavelengths = self._sp.wavelengths()
    #print (wavelengths[-10:])
    
    scans = []
    
    for i in range(0, scansToAverage):
      # get intensities - counts in spectrometertraSuite
      #t = timeit.default_timer()
      rawInt = self._sp.intensities(correctDarkCounts, correctNonlinearity)
      #log('single spectrum acq t: {0}'.format(timeit.default_timer() - t))
      #spectrum = readSpectrumFromFile('counts_1_100ms.txt')
      #print (rawInt)
      
      scans.append(rawInt)
      if callback:
        callback((i+1)/scansToAverage)
   
    # average the spectrum
    intensities = np.average(scans, axis=0)
    #print (intensities[0:10])
    
    # replace frist two pixels with the value of 3rd
    # in OceanView first three values are the same
    intensities[0] = intensities[1] = intensities[2]
    
    # perform boxcar averaging
    if boxcarWidth > 0:
      window = boxcarWidth*2 + 1
      intensities = np.convolve(intensities, np.ones(window), mode='same') / window
    
    return {
      'xs': self.wavelengths,
      'ys': intensities
    }
