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
    output: Annotated[str, typer.Option(help="Where to output the generated files. Defaults to package_directory/generated")] = None,        
    c: Annotated[bool, typer.Option(help="CMakeLists.txt")] = None,
    p: Annotated[bool, typer.Option(help="Generate package.xml")] = None):
    
    #Cross platform absolute path
    package_path=Path(package_directory).resolve()

    #Verify real directory
    if not package_path.exists():
        raise FileNotFoundError(f"Could not find {package_path} !")
    
    #Do both if args not specified
    if c==None and p==None:
        #Gen Both
        print("Generated CMakeLists and package.xml")
        pass
    else:
        # if c==True:
        #     #Gen cMake
        #     print("Generated CMakeLists.txt")
        #     pass
        if p==True:
            GENERATED_DIRECTORY=(package_path/"GENERATED").resolve()
            #Generate xml doc
            packageXMLGen=genPackageXML.PackageXMLGenerator()
            if output==None:
                output=GENERATED_DIRECTORY
            packageXMLGen.createPackageXML(package_path,Path(output))
            print("Generated package.xml")
            
    # with open(GENERATED_DIRECTORY+'CMakeLists.txt', 'w') as cmakelists_file:
    #     cmakelists_file.write(package_directory)



if __name__ == "__main__":
    app()