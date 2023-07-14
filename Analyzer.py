import Result
import os, sys
import numpy as np
import pandas as pd
from datetime import datetime

class Analyzer:

    def __init__(self):
        self.fResult = Result.Result()

    def getMetaData(self,metadata):
        print("This is a MaPSA")

    def getResult(self):
        return self.fResult

    def getRecentFile(self, filestring, name):

        files = os.popen('ls '+filestring).read().split()

        if len(files) < 1:
            print("Error: no files specified")
            return "0"

        elif len(files) == 1:
            return files[0]

        else:
            latestFileIndex = -1
            datetimeLatest = datetime.strptime('2000_01_01_01_00_00', '%Y_%m_%d_%H_%M_%S')

            for j, f in enumerate(files):

                dateString = f.split(name)[-1][1:20]
                datetimeObject = datetime.strptime(dateString, '%Y_%m_%d_%H_%M_%S')

                if datetimeObject > datetimeLatest:
                    latestFileIndex = j 
            return files[latestFileIndex]

    def analyze(self, testDir, moduleName):

        self.fResult.updateResult([moduleName],{})
        print('self.fResult=',self.fResult)

        logfilesAllChips = []

        NAbnormalCurrent = 0
        NUnmaskable = 0
        NNonOperational = 0
        NNonOperationalPerChip = ""
        NUnmaskablePerChip_dict = {}
        ItotPerChip = []
 
           
        for i in range(1,17):

            chipName = str(i)
            chipSearchString = moduleName + "_" + str(i)

            print(chipName)
            logfile = self.getRecentFile(testDir + '/log*_' + chipSearchString + '_*.log', chipSearchString)
            #print(logfile)
            logfilesAllChips += [logfile]

            # Current draw
            self.fResult.updateResult([moduleName,chipName],self.getCurrent(logfile,'Ianalog','P_ana'))
            self.fResult.updateResult([moduleName,chipName],self.getCurrent(logfile,'Idigital','P_dig'))
            self.fResult.updateResult([moduleName,chipName],self.getCurrent(logfile,'Ipad','P_pad'))
            self.fResult.updateResult([moduleName,chipName],self.getCurrent(logfile,'Itotal','Total: '))
            
            itotal = 200 #self.fResult.getResultValue([moduleName,chipName,'Itotal']) 
            Itot = self.getCurrent(logfile,'Itotal','Total: ')
            ItotPerChip.append(Itot['Itotal'])

            if itotal > 250 or itotal < 150:
                NAbnormalCurrent += 1

            # Pixel alive
            # number and list of dead, ineffient, noisy
            pafile = self.getRecentFile(testDir + '/mpa_test_'+ chipSearchString + '_*_pixelalive.csv', chipSearchString)
            
            #added
            print(pafile)
            #print(chipSearchString)
            
            self.fResult.updateResult([moduleName,chipName],self.getNumberAndList(pafile,'Dead'))
            self.fResult.updateResult([moduleName,chipName],self.getNumberAndList(pafile,'Inefficient'))
            self.fResult.updateResult([moduleName,chipName],self.getNumberAndList(pafile,'Noisy'))

            # Mask
            maskfile = self.getRecentFile(testDir + '/mpa_test_' + chipSearchString + '_*_mask_test.csv', chipSearchString)
            self.fResult.updateResult([moduleName,chipName],self.getNumberAndList(maskfile,'Unmaskable'))
            NUnmaskable += self.fResult.getResultValue([moduleName,chipName,'NUnmaskablePix'])

            # Noise and Pedestal
            noisefile = self.getRecentFile(testDir + '/mpa_test_' + chipSearchString + '_*_PostTrim_CAL_CAL_RMS.csv', chipSearchString)
            self.fResult.updateResult([moduleName,chipName],self.getMeanStdOutliers(noisefile,'Noise'))

            pedestalfile = self.getRecentFile(testDir + '/mpa_test_' + chipSearchString + '_*_PostTrim_CAL_CAL_Mean.csv', chipSearchString)
            self.fResult.updateResult([moduleName,chipName],self.getMeanStdOutliers(pedestalfile,'Pedestal'))

            #Number and list of Unmaskable pixels
            Unmaskable_dict = self.getNumberAndList(maskfile,'Unmaskable')
            print(Unmaskable_dict)
            NUnmaskablePerChip_dict[i] = Unmaskable_dict['NUnmaskablePix']
            # Bad bumps
            # number and list of bad bumps
            
            nonOperational = []
            for variable in ['DeadPix','InefficientPix','NoisyPix']: # Add untrimmable and bad bump
                nonOperational += self.fResult.getResultValue([moduleName,chipName,variable]).split(',')[:-1]
            
            nonOperational = np.unique(nonOperational)
            self.fResult.updateResult([moduleName,chipName],dict({'NNonOperational':len(nonOperational)}))
            NNonOperational += len(nonOperational)
            NNonOperationalPerChip += str(len(nonOperational))+','
            print('nonOperationalPix =', nonOperational)
            print('NNonOperational =', NNonOperational)
            
            PerChip_list = NNonOperationalPerChip.split(',')[:-1]
            Grade_list = np.zeros(len(PerChip_list),str)

            for n in range(len(PerChip_list)):
               if int(PerChip_list[n])<19:
                  Grade_list[n] = 'A'
               elif 19<=int(PerChip_list[n])<=94:
                  Grade_list[n] = 'B'
               elif int(PerChip_list[n])>94 or NUnmaskable !=0:
                  Grade_list[n] = 'C'
        
        NUnmaskablePerChip = list(NUnmaskablePerChip_dict.values())
        for m in range(len(NUnmaskablePerChip)):
           if int(NUnmaskablePerChip[m]) != 0:
              Grade_list[m] = 'C'
        ItotGrade = np.zeros(len(ItotPerChip),str)
        for t in range(len(ItotPerChip)):
           if ItotPerChip[t] > 100 and ItotPerChip[t] < 250:
              ItotGrade[t] = 'A'
           else:
              ItotGrade[t] = 'C'
        
        FinalMPAGrade = []
        for current, pix  in zip(ItotGrade, Grade_list):
           FinalMPAGrade.append(max(current, pix))

        print('\nSummary')
        print('ItotPerChip=', ItotPerChip)
        print('Itot Grade=', ItotGrade)
        print('NNonOperationalPerChip =', NNonOperationalPerChip)
        print('NUnmaskablePerchip=', NUnmaskablePerChip)
        print('Pixel Grade =',Grade_list)
        #print('\nMPA Grade=', FinalMPAGrade)  
        
        
        self.fResult.updateResult([moduleName,'NAbnormalCurrentChips'],NAbnormalCurrent)
        self.fResult.updateResult([moduleName,'NUnmaskablePix'],NUnmaskable)
        self.fResult.updateResult([moduleName,'NNonOperationalPix'],NNonOperational)
        self.fResult.updateResult([moduleName,'NNonOperationalPixPerChip'],NNonOperationalPerChip)
        
        
#        IVData = self.getIVScan(testDir + '/IVScan_'+moduleName+'.csv')
#        self.fResult.updateResult([moduleName,'Iat600V'],np.array(IVData[IVData['V']==-600]['I'])[0])
        #IV data, I grader
        IVfile = self.getRecentFile(testDir + '/IVScan_'+ moduleName + '_*.csv', moduleName)
        IVData = self.getIVScan(IVfile)
#        print(IVData)

        At800 = IVData[IVData['V'] == -800.0]
        Iat800 = At800['I'].to_string(index=False)
        print('Iat800=',Iat800)
        if float(Iat800)>0.00001:
           IVgrade = 'C'
        elif float(Iat800)>0.000001:
           IVgrade = 'B'
        else:
           IVgrade = 'A'
        print('IV Grade =', IVgrade)
        
        print('\nMPA Grade=', FinalMPAGrade)
        
        Grade_dict = {}
        Grade_dict[moduleName] = {}
        Grade_dict[moduleName]['MPA Grade'] = {}
        for c in range(0,16):
             Grade_dict[moduleName]['MPA Grade'][c+1] = FinalMPAGrade[c]
        Grade_dict[moduleName]['IV Grade'] = IVgrade
        
        #rework candidate
        C_counts = list(Grade_dict[moduleName]['MPA Grade'].values()).count('C')
        print("Number of grade 'C':", C_counts)
        if C_counts in (1,2,3) and Grade_dict[moduleName]['MPA Grade']['IV Grade'] == 'A':
            Grade_dict[moduleName]['Rework'] = 'Yes'
        else:
            Grade_dict[moduleName]['Rework'] = 'No'
        
        mpa_grade_values = list(Grade_dict[moduleName]['MPA Grade'].values())
        iv_grade = Grade_dict[moduleName]['IV Grade']

        total_grade = max(max(mpa_grade_values), iv_grade)
        Grade_dict[moduleName]['MaPSA Grade'] = total_grade

        print('Grade =', Grade_dict)

    def getCurrent(self, logfile, varname, tag):
        returnDict = {}
        if len(logfile) <= 1:
            return returnDict

        cmd = "grep " + tag + " " + logfile
        x = os.popen(cmd).read()
        x = x.replace('I= ', 'CUT')
        x = x.replace(' mA', 'CUT')
        y = x.split('CUT')
        I = float(y[1])

        # Add it to the dict
        returnDict[varname] = I
       

        return returnDict
        
    # Description
    def getNumberAndList(self, datafile, varname, threshold=5):
        returnDict = {}

        if len(datafile) <= 1:
            return returnDict

        data = np.genfromtxt(datafile, delimiter=',')[:,1][1:]

        if varname == 'Dead':
            indices = np.where(data==0)[0]
            
        elif varname == "Inefficient":
            indices = np.where((data<100) & (data>0))[0]

        elif varname == "Noisy":
            indices = np.where((data>100))[0]

        elif varname == "Unmaskable":
            indices = np.where(data > 0)[0]

        pixelString = ""
        for i in indices:
            pixelString += str(i)+","

        returnDict["N"+varname+"Pix"] = len(indices)
        returnDict[varname+"Pix"] = pixelString

        
        return returnDict
        
    # Extract useful info about noise given the part name and hist of noise / channel
    def getMeanStdOutliers(self, datafile, varname, threshold=5):
        # threshold = number of sigma away from mean that qualifies as "outlier"
        returnDict = {}

        if len(datafile) <= 1:
            return returnDict

        data = np.genfromtxt(datafile, delimiter=',', dtype='float')[:,1][1:]

        mean = np.mean(data)
        std  = np.std(data)

        returnDict[varname+"Mean"] = mean
        returnDict[varname+"Std"] = std
        
        # calculate outliers                                                                                                  
        outliersHigh = []
        outliersLow = []
        for i, d in enumerate(data):
            if d > mean + threshold * std:
                outliersHigh.append(i)
            if d < mean - threshold * std:
                outliersLow.append(i)

        outliersLowString = ""
        for strip in outliersLow:
            outliersLowString += str(strip)+","
        returnDict[varname+"NOutliersLow"] = len(outliersLow)
        returnDict[varname+"OutliersLow"] = outliersLowString

        outliersHighString = ""
        for strip in outliersHigh:
            outliersHighString += str(strip)+","
        returnDict[varname+"NOutliersHigh"] = len(outliersHigh)
        returnDict[varname+"OutliersHigh"] = outliersHighString

        return returnDict
        
    # Extract useful info about the IV scan
    def getIVScan(self, IVFile):
        data = pd.read_csv(IVFile,delimiter=',',header=None, names = ['V','I'])
        df = pd.DataFrame(data)
        #df['V'] = df['VI'].str.split(',').str[0]
        #df['I'] = df['VI'].str.split(',').str[1]
        return df
        

        #return pd.read_csv(IVFile,delimiter='\t',header=None,names=['V','I'])

