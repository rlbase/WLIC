import pandas

def readSpectrumFromFile(filename):
  file = open(filename, mode='r')
  lines = file.readlines()
  file.close()

  xs = []
  ys = []
  
  insideData = False
  
  for i in range (0, len(lines)):
    if lines[i].startswith('>>>>>End'):
      insideData = False
      break
    
    if lines[i].startswith('>>>>>Begin'):
      insideData = True
      continue
    
    if insideData:
      line = lines[i].rstrip('\r\n').replace(',', '.').split("\t")
      xs.append(float(line[0]))
      ys.append(float(line[1]))
    
  return {'xs': xs, 'ys': ys}

def readCalibrationFile(filename):
  file = open(filename, mode='r')
  lines = file.readlines()
  file.close()
  
  xs = []
  ys = []

  for i in range (9, len(lines)):
    line = lines[i].rstrip('\r\n').split("\t")
    xs.append(float(line[0]))
    ys.append(float(line[1]))
    
  return {'xs': xs, 'ys': ys}

def readFileSimple(filename):
  file = open(filename, mode='r')
  lines = file.readlines()
  file.close()
  
  xs = []

  for i in range (0, len(lines)):
    line = lines[i].rstrip('\r\n')
    xs.append(float(line))
       
  return xs

def writeSpectrumToFile(spectrum, filePath):
  df = pandas.DataFrame(spectrum)
  with open(filePath, 'w', newline='') as f:
    df.to_csv(f, sep='\t', columns=['xs', 'ys'], index=False, header=False)
    
  return