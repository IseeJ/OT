class Result():

    def __init__(self):
        self.fResultDict = {}
        self.fPart = 0
        self.fRun = 0

    def updateResult(self, keywords, value):

        thisDict = self.fResultDict
        for i,key in enumerate(keywords):

            # Loop down through levels of dictionary specified in keywords arg
            if i != len(keywords) - 1:
                thisDict = thisDict[key]

            # At lowest level
            else:
                # if we want to update with a dictionary
                if type(value) is dict:
                    # if the dictionary we want to update exists
                    # update it
                    if key in thisDict.keys():
                        thisDict[key].update(value)
                    # if the dictionary we want to update does not exist
                    # create an empty one and update it
                    else:
                        thisDict[key] = {}
                        thisDict[key].update(value)
                # if we want to update with a value
                else:
                    thisDict[key] = value
                
    def getResultValue(self, keywords):
        theDict = self.fResultDict
        #print(keywords)
        #print(theDict)
        #print(theDict['HPK_35494_002R']['1'].keys())

        for key in keywords:	
            theDict = theDict[key]
        #print(type(theDict))
        return theDict
