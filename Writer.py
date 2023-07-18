import Result

class Writer:
    
    def writeResultToXML(self, result, outputXMLFile):
        print("Writing result to " + outputXMLFile)

        # install in venv using
        # pip install dict2xml
        from dict2xml import dict2xml
        import xml.etree.ElementTree as ET
        def dict_to_xml(data, parent):
            for key, value in data.items():
                if isinstance(value, dict):
                    element = ET.SubElement(parent, key)
                    dict_to_xml(value, element)
                else:
                    element = ET.SubElement(parent, key)
                    element.text = str(value)
        root = ET.Element("ROOT")
        dict_to_xml(result.fResultDict,root)
        tree = ET.ElementTree(root)
        ET.indent(tree, space="    ", level=0)
        tree.write(outputXMLFile, encoding="utf-8", xml_declaration=True, method="xml")
        print("XML saved to output.xml")
        

        #dict2xml
        xml = dict2xml(result.fResultDict, indent ="   ")
        outputFile = open(outputXMLFile+'2', "w")
        outputFile.write(xml)
        outputFile.close()

    def writeResultToHTML(self, result, outputHTMLFile):
        print("Writing result to HTML")
        
    def writeScoreToXML(self, score, outputXMLFile):
        print("Writing score to XML")

    def writeScoreToHTML(self, score, outputHTMLFile):
        print("Writing score to HTML")
        
                

    
