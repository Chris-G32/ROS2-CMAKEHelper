import json
import os



class PackageXMLGenerator:
    def __init__(self):
        self.config = {}

    def load_config(self):
        CONFIG_FILE = "xmlConfig.json"
        with open(CONFIG_FILE, "r") as file:
            self.config = json.load(file)

    def getMessageDependencies(self):
        return "<buildtool_depend>rosidl_default_generators</buildtool_depend>\
  <exec_depend>rosidl_default_runtime</exec_depend>\
  <member_of_group>rosidl_interface_packages</member_of_group>"
    
    def inferDependecies(self,package_directory=None):
        dependencies='<depend>rclcpp</depend>\n'
        # os.listdir(os.getcwd())
        
        return dependencies
    # Due to ros constraints, parent folder should be the same as the package directory
    def generate(self, package_directory, msg_package=False):
        self.load_config()
        name = self.config["name"]
        maintainer_email = self.config["maintainer_email"]

        msg_dependencies = ""
        #Eventually add inference of msg package
        if msg_package == True:
            #Include message dependencies
            msg_dependencies = self.getMessageDependencies()
        
        #Infer package dependencies by includes
        inferred_dependencies=self.inferDependecies()

        #Document to write
        XML_FRAME = f'<?xml version="1.0"?>\
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>\
<package format="3">\
  <name>{package_directory.lower()}</name>\
  <version>0.0.0</version>\
  <description>TODO: Package description</description>\
  <maintainer email="{maintainer_email}">{name}</maintainer>\
  <license>TODO: License declaration</license>\
  <buildtool_depend>ament_cmake</buildtool_depend>\
  <test_depend>ament_lint_auto</test_depend>\
  <test_depend>ament_lint_common</test_depend>\
  {msg_dependencies}\
  {inferred_dependencies}\
  <export>\
    <build_type>ament_cmake</build_type>\
  </export>\
</package>'
        return XML_FRAME
