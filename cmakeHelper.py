import typer
import os
from typing_extensions import Annotated
import genPackageXML
import xml.etree.ElementTree as ET

from pathlib import Path

app=typer.Typer()

@app.command()
def hello(name: str):
    print(f"Hello {name}")

@app.command(help="Generates and outputs the cmakelists.txt and package.xml files")
def generate(package_directory: str,
    c: Annotated[bool, typer.Option(help="CMakeLists.txt")] = None,p: Annotated[bool, typer.Option(help="Generate package.xml")] = None):
    
    #Cross platform absolute path
    package_path=Path(package_directory)

    #Verify real directory
    if not package_path.exists():
        raise FileNotFoundError(f"Could not find {package_directory} !")
    
    #Directory for generated files
    GENERATED_DIRECTORY=package_directory+"GENERATED/"
    #Make the generated dir if it doesnt exist
    os.makedirs(package_directory+GENERATED_DIRECTORY,exist_ok=True)

    #Do both if args not specified
    if c==None and p==None:
        #Gen Both
        print("Generated CMakeLists and package.xml")
        pass
    else:
        if c==True:
            #Gen cMake
            print("Generated CMakeLists.txt")
            pass
        if p==True:
            #Gen package xml
            print("Generated package.xml")
            #Generate xml doc
            packageXMLGen=genPackageXML.PackageXMLGenerator()
            xmlStr=packageXMLGen.generate(package_directory)

            #Make it look nice
            element=ET.XML(xmlStr)
            ET.indent(element)

            #Save to file
            with open(GENERATED_DIRECTORY+'package.xml', 'w') as package_xml_file:
                package_xml_file.write(ET.tostring(element, encoding='unicode'))
            
    with open(GENERATED_DIRECTORY+'CMakeLists.txt', 'w') as cmakelists_file:
        cmakelists_file.write(package_directory)



if __name__ == "__main__":
    app()