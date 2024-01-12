import json
import os
from pathlib import Path
from dependency_handler import DependencyHandler
import re
import xml.etree.ElementTree as ET

#This handles dependency deduction for the packageXML files
class XMLDepHandler(DependencyHandler):
    def __init__(self, ros_version):
        super().__init__()

    def getMessageDependencies(self):
        return "<buildtool_depend>rosidl_default_generators</buildtool_depend>\
                <exec_depend>rosidl_default_runtime</exec_depend>\
                <member_of_group>rosidl_interface_packages</member_of_group>"

    def get_includes(self, file_path: Path):
        # Regex that matches includes
        include_pattern = re.compile(r'^\s*#include\s*["](.+)["]\s*$')
        includes = set()

        with open(file_path, 'r') as file:
            for line in file:
                match = include_pattern.match(line)
                if match:
                    includes.add(match.group(1))
        return includes

    def getSourceDependencies(self, directory: Path):
        included_packages = set()
        for x in directory.iterdir():
            if x.is_dir():
                return self.getSourceDependencies(x)
            else:
                includes = self.get_includes(x.resolve())
                included_packages = included_packages.union(includes)
        return included_packages

    def purgeNonPackages(self, package_directory: Path, includes: set):
        package_candidates = []

        for item in includes:
            split = item.split('/')
            if len(split) > 1:
                package_candidates.append(split[0])

        parent_directory = package_directory.parent

        if not parent_directory.exists():
            return []

        shared_directories = set()
        for cand in package_candidates:
            isROSPKG = (Path('/opt/ros/humble/share') / cand).exists()
            isLocalPKG = (parent_directory / cand).exists()
            if isLocalPKG or isROSPKG:
                shared_directories.add(cand)

        return shared_directories

    def inferDependecies(self, package_directory: Path):
        directories = [x for x in package_directory.iterdir() if x.is_dir()]
        self.setFlags(directories)
        msg_dependencies = ""
        
        if self.get_custom_message_folder_flag() or self.get_custom_service_folder_flag():
            msg_dependencies = self.getMessageDependencies()

        src_dependencies = set()
        if self.get_includes_folder_flag():
            includePath = package_directory / "include" / package_directory.stem
            assert includePath.exists(), 'Include path is not formatted properly, directory should be of form include/package_name/files.extension'
            src_dependencies = src_dependencies.union(self.getSourceDependencies(includePath))

        if self.get_source_folder_flag():
            src_dependencies = src_dependencies.union(self.getSourceDependencies(package_directory / 'src'))

        package_dependencies = self.purgeNonPackages(package_directory.resolve(), src_dependencies)
        package_dep_str = ''

        for i in package_dependencies:
            if i != package_directory.stem:
                package_dep_str += f"<depend>{i}</depend>"

        dependencies = f'{msg_dependencies}{package_dep_str}'
        return dependencies


class PackageXMLGenerator:
    def __init__(self):
        self.config = {}
        self.msg_dependencies = ""

    def load_config(self):
        CONFIG_FILE = "xmlConfig.json"
        with open(CONFIG_FILE, "r") as file:
            self.config = json.load(file)

    def generate(self, package_directory: Path):
        self.load_config()
        name = self.config["name"]
        maintainer_email = self.config["maintainer_email"]
        inferred_dependencies = XMLDepHandler(self.config['ros_version']).inferDependecies(package_directory)
        package_name = package_directory.stem

        XML_FRAME = f'<?xml version="1.0"?>\
                    <?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>\
                    <package format="3">\
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

    def createPackageXML(self, package_directory: Path, outputTo: Path):
        XML_HEADING = '<?xml version="1.0"?>\n\
                       <?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>\n'
        xmlStr = self.generate(package_directory)
        element = ET.XML(xmlStr)
        ET.indent(element)
        os.makedirs(outputTo, exist_ok=True)

        with open(outputTo / 'package.xml', 'w') as package_xml_file:
            package_xml_file.write(XML_HEADING)
            package_xml_file.write(ET.tostring(element, encoding='unicode'))
