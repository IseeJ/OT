import os, sys
#import MakeModulePlots

import Analyzer
#import Writer

def main():

    name = sys.argv[1]

    # Analysis
    print("Here I would do analysis")
    analyzer = Analyzer.Analyzer()
    testDir = "/uscms/home/jennetd/nobackup/outer-tracker/mapsa-round3/Results_MPATesting/"+name
    analyzer.analyze(testDir,name)

    result = analyzer.getResult()
   

    # XML
#    print("Creating XML file for MaPSA "+name)

#    writer = Writer.Writer()
#    outputXML = "../XML/"+name+".xml"
#    writer.writeResultToXML (result, outputXML )
    
    # Summary plots with Hannsjoerg's code
#    print("Drawing summary plots for MaPSA "+name)
#    PlotAllPlotsModulesAutomated(name, show_plot=False, save_plot=True)


if __name__ == "__main__":
    main()
