import json
from pathlib import Path
from dependency_handler import DependencyHandler

class CMAKEDepHandler(DependencyHandler):
    def __init__(self) -> None:
        super().__init__()
    def inferDependecies(self,package_directory:Path):
        source_dependencies=self.inferSourceDependencies(package_directory)


class CMAKEListsGenerator:
    def __init__(self):
        self.config = {}

    def load_config(self):
        CONFIG_FILE = "xmlConfig.json"
        with open(CONFIG_FILE, "r") as file:
            self.config = json.load(file)

    def generate(self, package_directory: Path):
        #Load config from file
        self.load_config()
        #Dev info
        name = self.config["name"]
        maintainer_email = self.config["maintainer_email"]
        #Get dependencies from fiels
        inferred_dependencies = CMAKEDepHandler().inferDependecies(package_directory)
        package_name = package_directory.stem #Package name must be the stem of the directory
        CMAKE_HEAD=f'cmake_minimum_required(VERSION 3.8)\
project({package_directory.stem})\
if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")\
  add_compile_options(-Wall -Wextra -Wpedantic)\
endif()'
        #Body of the xml
        CMAKE_FRAME = f'<package format="3">\
                            <name>{package_name}</name>\
                            <version>0.0.0</version>\
                            <description>TODO: Package description</description>\
                            <maintainer email="{maintainer_email}">{name}</maintainer>\
                            <license>TODO: License declaration</license>\
                            <buildtool_depend>ament_cmake</buildtool_depend>\
                            <test_depend>ament_lint_auto</test_depend>\
                            <test_depend>ament_lint_common</test_depend>\
                            {inferred_dependencies}\
                            <export>\
                                <build_type>ament_cmake</build_type>\
                            </export>\
                        </package>'
        return XML_FRAME
    
    def createCMakeLists(self, package_directory: Path, outputTo: Path):
        #The heading used in ros humble package XML, may vary but idk or care
        XML_HEADING = '<?xml version="1.0"?>\n<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>\n'
        #Generate the xml body for the package
        xmlStr = self.generate(package_directory)
        #Convert it into xml ob for formatting
        element = ET.XML(xmlStr)
        ET.indent(element)#Format

        #Create output dir if it doesnt exist
        os.makedirs(outputTo, exist_ok=True)

        #Write file
        with open(outputTo/'package.xml', 'w') as package_xml_file:
            package_xml_file.write(XML_HEADING)
            package_xml_file.write(ET.tostring(element, encoding='unicode'))
        a=str()
        a.find