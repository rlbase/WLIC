#!/usr/bin/env python
# -*- coding: utf-8 -*-

## Author: Peter Nadrah
## License: GNU GPL v3
## Description: Part of WLIC - simple GUI program for collecting spectra from
##              spectrometer.

## 0.1, 13.01.2023
##   First version, based on gui for fluorescence measurement.
## 0.2, 13.01.2023
##   Fixed three pixels/values of spectrum. Updated light/dark spectra.
##   Works for basic measurement. No file saving yet.
##
##

import time
import tkinter as tk
from tkinter import ttk
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.figure as figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk
)
from read_files import *
from spcomm import *
#from irradiance import *
import numpy as np

# default values
_defaults = {
  'integrationTime': 10000, # in microseconds
  'collectionArea': 0.40018986, # in cm^2
  'scansToAverage': 4,
  'boxcarWidth': 0, # to the left and right, for averaging
  'correctDarkCounts': True,
  'correctNonlinearity': True  
}

_data = {
  'darkSpectrum': None,
  'lightSpectrum': None
}

def setupWindow():
  global _s
  global app
  global spectrometer
  
  app = {}
  app['window'] = tk.Tk()
  app['mainFrame'] = tk.Frame(app['window'])
  app['mainFrame'].grid(column=0, row=0)
  
  app['settingsFrame'] = tk.Frame(
    app['mainFrame'],
    padx=2,
    pady=2,
  )
  app['settingsFrame'].grid(column=0, row=0, sticky=tk.W+tk.E+tk.N)
  
  app['viewFrame'] = tk.Frame(app['mainFrame'])
  app['viewFrame'].grid(column=1, row=0)
  
  app['figureFrame'] = tk.Frame(app['viewFrame'])
  app['figureFrame'].grid(column=0, row=0)

  app['window'].geometry('900x700+300+0')
  app['window'].title('WLIC')
  app['window'].config(bg='#FFFFFF')
  app['window'].resizable(width=True, height=True)
  
  app['samples'] = []
  
  """
  hierarchy of the left panel:
  
  settings
    continuous light s.
    measurement s.
      light/ex s.
      spectrometer/em s.
      timing s.
      samples s.
    load settings
  
  """
  """
  _s = {
    'integrationTime': tk.IntVar(app['window'], _defaults['integrationTime']),
    'scansToAverage': tk.IntVar(app['window'], _defaults['scansToAverage']),
    'boxcarWidth': tk.IntVar(app['window'], _defaults['boxcarWidth']),
    'correctDarkCounts': tk.BooleanVar(app['window'], _defaults['correctDarkCounts']),
    'correctNonlinearity': tk.BooleanVar(app['window'], _defaults['correctNonlinearity'])
  }
  """
  _s = {
    'integrationTime': _defaults['integrationTime'],
    'scansToAverage': _defaults['scansToAverage'],
    'boxcarWidth':  _defaults['boxcarWidth'],
    'correctDarkCounts': tk.BooleanVar(app['window'], _defaults['correctDarkCounts']),
    'correctNonlinearity': tk.BooleanVar(app['window'], _defaults['correctNonlinearity'])
  }

  ### spectrometer settings ###
  
  spectrometerSettingsFrame = tk.LabelFrame(
    app['settingsFrame'],
    text = 'spectrometer settings',
    padx=2,
    pady=2
  )
  spectrometerSettingsFrame.grid(column=0, row=0, sticky=tk.W+tk.E+tk.N)
  
  rowIndex = 0
  
  acqTimeLabel = tk.Label(
    spectrometerSettingsFrame,
    text='time [us]:'
  )
  acqTimeLabel.grid(column=0, row=rowIndex, sticky=tk.W)
  
  app['acqTimeTextBox'] = tk.Text(
    spectrometerSettingsFrame,
    width=10,
    height=1
  )
  app['acqTimeTextBox'].grid(column=1, row=rowIndex, sticky=tk.W)
  #acqTimeTextBox.insert('1.0', spData['integrationTime'])
  app['acqTimeTextBox'].insert('1.0', _s['integrationTime'])
  
  rowIndex += 1
  
  acqScansLabel = tk.Label(
    spectrometerSettingsFrame,
    text='scans:'
  )
  acqScansLabel.grid(column=0, row=rowIndex, sticky=tk.W)
  
  app['acqScansTextBox'] = tk.Text(
    spectrometerSettingsFrame,
    width=10,
    height=1
  )
  app['acqScansTextBox'].grid(column=1, row=rowIndex, sticky=tk.W)
  #acqScansTextBox.insert('1.0', spData['scansToAverage'])
  app['acqScansTextBox'].insert('1.0', _s['scansToAverage'])
  
  rowIndex += 1
  acqBoxcarLabel = tk.Label(
    spectrometerSettingsFrame,
    text='boxcar width:'
  )
  acqBoxcarLabel.grid(column=0, row=rowIndex, sticky=tk.W)
  
  app['acqBoxcarTextBox'] = tk.Text(
    spectrometerSettingsFrame,
    width=10,
    height=1
  )
  app['acqBoxcarTextBox'].grid(column=1, row=rowIndex, sticky=tk.W)
  app['acqBoxcarTextBox'].insert('1.0', _s['boxcarWidth'])

  rowIndex += 1
  acqCorrDarkLabel = tk.Label(
    spectrometerSettingsFrame,
    text='correct dark pixels:'
  )
  acqCorrDarkLabel.grid(column=0, row=rowIndex, sticky=tk.W)
  acqCorrDarkCheckbox = tk.Checkbutton(
    spectrometerSettingsFrame,
    onvalue=1,
    offvalue=0,
    variable=_s['correctDarkCounts']
  )
  acqCorrDarkCheckbox.grid(column=1, row=rowIndex, sticky=tk.W)
  
  rowIndex += 1
  acqNonLinCorrLabel = tk.Label(
    spectrometerSettingsFrame,
    text='non-lin corr.:'
  )
  acqNonLinCorrLabel.grid(column=0, row=rowIndex, sticky=tk.W)
  acqNonLinCorrCheckbox = tk.Checkbutton(
    spectrometerSettingsFrame,
    onvalue=1,
    offvalue=0,
    variable=_s['correctNonlinearity']
  )
  acqNonLinCorrCheckbox.grid(column=1, row=rowIndex, sticky=tk.W)
  
  
  ### sample settings ###
  
  sampleSettingsFrame = tk.LabelFrame(
    app['settingsFrame'],
    text = 'sample settings',
    padx=2,
    pady=2
  )
  sampleSettingsFrame.grid(column=0, row=3, sticky=tk.W+tk.E)
  
  rowIndex = 0
  selectDirectoryButton = tk.Button(
    sampleSettingsFrame,
    text='select dir',
    #font=('times 14'),
    borderwidth=1,
    relief='solid',
    command=selectDirectory
  )
  selectDirectoryButton.grid(column=0, row=rowIndex, columnspan=2, sticky=tk.E)
  
  rowIndex += 1
  directoryLabel = tk.Label(
    sampleSettingsFrame,
    text='dir:'
  )
  directoryLabel.grid(column=0, row=rowIndex, sticky=tk.W)
  directoryValueLabel = tk.Label(
    sampleSettingsFrame,
    #textvariable=saveFileData['dir']
    #textvariable=saveFileData['dir']
  )
  directoryValueLabel.grid(column=1, row=rowIndex, sticky=tk.W)
  
  rowIndex += 1
  sampleNameLabel = tk.Label(
    sampleSettingsFrame,
    text='sample name:'
  )
  sampleNameLabel.grid(column=0, row=rowIndex, sticky=tk.W)
  
  sampleNameTextBox = tk.Text(
    sampleSettingsFrame,
    width=20,
    height=1,
  )
  sampleNameTextBox.grid(column=1, row=rowIndex, sticky=tk.W)
  
  rowIndex += 1
  app['measureButton'] = tk.Button(
    sampleSettingsFrame,
    text='measure',
    borderwidth=1,
    relief='solid',
    command=measureButtonClick
  )
  app['measureButton'].grid(column=0, row=rowIndex, columnspan=2, sticky=tk.E)
  
  rowIndex += 1
  app['measureDarkButton'] = tk.Button(
    sampleSettingsFrame,
    text='measure dark',
    borderwidth=1,
    relief='solid',
    command=measureDarkButtonClick
  )
  app['measureDarkButton'].grid(column=0, row=rowIndex, columnspan=2, sticky=tk.E)

  rowIndex += 1
  app['infoLabelText'] = tk.StringVar(value='idle')
  infoLabel = tk.Label(
    sampleSettingsFrame,
    textvariable=app['infoLabelText']
  )
  infoLabel.grid(column=0, row=rowIndex, sticky=tk.W)
 
 ### irradiance ###
  
  irradianceFrame = tk.LabelFrame(
    app['settingsFrame'],
    text = 'irradiance',
    padx=2,
    pady=2
  )
  irradianceFrame.grid(column=0, row=4, sticky=tk.W+tk.E)
  
  rowIndex = 0
  wlLimitsLabel = tk.Label(
    irradianceFrame,
    text='wl limits:'
  )
  wlLimitsLabel.grid(column=0, row=rowIndex, sticky=tk.W)
  
  app['wlLimitsMinTextBox'] = tk.Text(
    irradianceFrame,
    width=10,
    height=1,
  )
  app['wlLimitsMinTextBox'].grid(column=1, row=rowIndex, sticky=tk.W)
  
  wlLimitsDashLabel = tk.Label(
    irradianceFrame,
    text='-'
  )
  wlLimitsDashLabel.grid(column=2, row=rowIndex, sticky=tk.W)
  
  app['wlLimitsMaxTextBox'] = tk.Text(
    irradianceFrame,
    width=10,
    height=1,
  )
  app['wlLimitsMaxTextBox'].grid(column=3, row=rowIndex, sticky=tk.W)
  
  rowIndex += 1
  app['calcIrradianceButton'] = tk.Button(
    irradianceFrame,
    text='calculate irradiance',
    borderwidth=1,
    relief='solid',
    command=calcIrradianceButtonClick
  )
  app['calcIrradianceButton'].grid(column=0, row=rowIndex, columnspan=4, sticky=tk.E)
  
  # from main py file
  resultTextBox = tk.Text(
    app['viewFrame'],
    height=8,
    #font=('times 14'),
    bg='#FFFFFF'
  )
  resultTextBox.grid(column=0, row=5, sticky=(tk.N, tk.S))

  actionButtonFrame = tk.Frame(
    app['settingsFrame'],
    bg='#FFFFFF'
  )
  actionButtonFrame.grid(column=0, row=6)
  
  """
  measureDarkButton = tk.Button(
    actionButtonFrame,
    text='izmeri spekter v temi',
    #font=('times 14'),
    bg='#CCCCCC',
    padx=5,
    pady=2,
    borderwidth=1,
    relief='solid',
    command=measureDarkButtonClick
  )
  measureDarkButton.grid(column=0, row=0, padx=5, pady=2)
  """
  
  figureButtonFrame = tk.Frame(app['viewFrame'])
  figureButtonFrame.grid(column=0, row=1)
  
  # https://matplotlib.org/stable/gallery/user_interfaces/embedding_in_tk_sgskip.html
  app['figure'] = matplotlib.figure.Figure(figsize=(6, 3), dpi=100, layout='tight')
  figureCanvas = FigureCanvasTkAgg(app['figure'], app['figureFrame'])
  figureToolbar = NavigationToolbar2Tk(figureCanvas, app['figureFrame'])
  
  app['axes'] = app['figure'].add_subplot(111)
  #axes.plot(pWls, spData['darkSpectrum']['ys'])
  lgd =  app['axes'].legend(loc=2, bbox_to_anchor=(1., 1.))
  lgd.get_frame().set_edgecolor('white')
  figureCanvas.get_tk_widget().pack(side=tk.TOP)
  
  #figureFrame.grid(column=0, row=0)
  
  app['figureRadioButtons'] = tk.IntVar()
  
  showDarkSpectrum = tk.Radiobutton(
    figureButtonFrame,
    text='dark spectrum',
    value=0,
    variable=app['figureRadioButtons'],
    bg='#FFFFFF',
    padx=5,
    pady=2,
    command=showSpectrumClick
  )
  showDarkSpectrum.grid(column=1, row=0)
  
  showLightSpectrum = tk.Radiobutton(
    figureButtonFrame,
    text='light spectrum',
    value=1,
    variable=app['figureRadioButtons'],
    bg='#FFFFFF',
    padx=5,
    pady=2,
    command=showSpectrumClick
  )
  showLightSpectrum.grid(column=2, row=0)
  
  showDiffSpectrum = tk.Radiobutton(
    figureButtonFrame,
    text='difference',
    value=2,
    variable=app['figureRadioButtons'],
    bg='#FFFFFF',
    padx=5,
    pady=2,
    command=showSpectrumClick
  )
  showDiffSpectrum.grid(column=3, row=0)
  """
  showIrradianceSpectrum = tk.Radiobutton(
    figureButtonFrame,
    text='irradiance',
    value=3,
    variable=app['figureRadioButtons'],
    bg='#FFFFFF',
    padx=5,
    pady=2,
    command=showSpectrumClick
  )
  showIrradianceSpectrum.grid(column=4, row=0)
  """
  app['window'].rowconfigure(2, weight=1)
 
  app['figureRadioButtons'].set(-1)
  showSpectrumClick()
  
  spectrometer = SpComm()
  spectrometer.connectToDevice()
  spectrometer.calculateWavelengths()
  
  """
  # testing
  spFilename = '2_Philips_label_down_25cm_20ms_16sc_0boxc_eld_nlc-on_USB2F017011__2__07-44-28-452.txt'
  darkSpFilename = '2_Philips_label_down_25cm_20ms_16sc_0boxc_eld_nlc-dark_USB2F017011__0__07-42-11-201.txt'
  
  _data['lightSpectrum'] = readSpectrumFromFile(spFilename)
  _data['darkSpectrum'] = readSpectrumFromFile(darkSpFilename)
  
  _s['integrationTime'] = 20000
  """
  
  
  app['window'].mainloop()
  
def selectDirectory():
  global saveFileData
  # testing
  #filename =  tk.filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("jpeg files","*.jpg"),("all files","*.*")))
  saveFileData['dir'].set(tk.filedialog.askdirectory())
  #print(saveFileData['dir'])

def addSample(app, sampleSettingsFrame, rowIndex):
  global samplesInfoFrame
  #global samples
  #global app
  # add controls
  
  nextCounter = len(app['samples'])
  
  sample = {
    'measurements': []
  }
  
  # IDs start from 1, counter from 0, yea...
  sample['id'] = nextCounter + 1
  
  sample['labelTextBox'] = tk.Text(
    sampleSettingsFrame,
    height=1,
    width=20
  )
  sample['labelTextBox'].grid(column=0, row=rowIndex+nextCounter)
  
  """
  sample['measureButton'] = tk.Button(
    samplesInfoFrame,
    text='meas. s. ' + str(sample['id']),
    borderwidth=1,
    relief='solid',
    #command=lambda: measureSample(nextCounter)
  )
  sample['measureButton'].grid(column=1, row=nextCounter, padx=5, pady=2)
  """
  
  app['samples'].append(sample)

def measureButtonClick():
  global _data
  
  sp = getSpectrum()
  _data['lightSpectrum'] = sp
  
  # update plot
  #updateFigure(sp)
  showSpectrumClick()
  
def measureDarkButtonClick():
  global _data
  
  sp = getSpectrum()
  _data['darkSpectrum'] = sp
  
  # update plot
  #updateFigure(sp)
  showSpectrumClick()
  
def calcIrradianceButtonClick():
  global _defaults
  global _data
  global _s
  
  if _data['lightSpectrum'] == None or _data['darkSpectrum'] == None:
    return
  
  calibration = readCalibrationFile('USB2+F01701_031209.IrradCal')
  
  wlWidths = calcWlWidths(_data['lightSpectrum']['xs'])
  irrad = calcIrradiance(_data['lightSpectrum'], _data['darkSpectrum'], calibration, _s['integrationTime'], _defaults['collectionArea'], wlWidths)
  
  minLimit = float(app['wlLimitsMinTextBox'].get('1.0', tk.END).strip())
  maxLimit = float(app['wlLimitsMaxTextBox'].get('1.0', tk.END).strip())
  
  regions = [{'min': minLimit, 'max': maxLimit, 'irradiance': 0.0}]
  regionsIrrad = calcIrradianceForRegions(irrad, regions, wlWidths)
  
  print (regionsIrrad)
  
  
def getSpectrum():
  global _s
  global app
  global spectrometer
  
  # retrieve and set settings
  _s['integrationTime'] = int(app['acqTimeTextBox'].get('1.0', tk.END).strip())
  _s['scansToAverage'] = int(app['acqScansTextBox'].get('1.0', tk.END).strip())
  _s['boxcarWidth'] = int(app['acqBoxcarTextBox'].get('1.0', tk.END).strip())
  #print('measureButtonClick', _s['integrationTime'], _s['scansToAverage'], _s['boxcarWidth'], _s['correctDarkCounts'].get(), _s['correctNonlinearity'].get())
  
  # get spectrum
  spectrometer.setIntegrationTime(_s['integrationTime'])
  time.sleep(float(_s['integrationTime'] / 1000000))
  sp = spectrometer.readSpectrumFromDevice(_s['scansToAverage'], _s['boxcarWidth'], _s['correctDarkCounts'].get(), _s['correctNonlinearity'].get())
  
  return sp
  
def updateFigure(data):
  global app
  
  app['axes'].cla()
  app['axes'].plot(data['xs'], data['ys'], marker='', linewidth=0.5)
  app['figure'].canvas.draw()
  app['figure'].canvas.flush_events()
  
def showSpectrumClick():
  global app
  global _data
  
  #print ('figureRadioButtons.get()', figureRadioButtons.get())
  #axes.cla()

  #if not 'pWls' in _data:
  if app['figureRadioButtons'].get() == 0:
    if 'ys' in _data['darkSpectrum']:
      updateFigure({'xs': _data['darkSpectrum']['xs'], 'ys': _data['darkSpectrum']['ys']})
  elif app['figureRadioButtons'].get() == 1:
    if 'ys' in _data['lightSpectrum']:
      updateFigure({'xs': _data['lightSpectrum']['xs'], 'ys': _data['lightSpectrum']['ys']})
  elif app['figureRadioButtons'].get() == 2:
    if 'ys' in _data['darkSpectrum'] and 'ys' in _data['lightSpectrum']:
      updateFigure({'xs': _data['lightSpectrum']['xs'], 'ys': np.subtract(_data['lightSpectrum']['ys'], _data['darkSpectrum']['ys'])})
  #elif app['figureRadioButtons'].get() == 3:
  #  if 'ys' in _data['irradianceSpectrum']:
  #    updateFigure({'xs': _data['pWls'], 'ys': _data['irradianceSpectrum']['ys']})
  
  #figure.canvas.draw()
  #figure.canvas.flush_events()
  return

if __name__ == '__main__':
  setupWindow()
  