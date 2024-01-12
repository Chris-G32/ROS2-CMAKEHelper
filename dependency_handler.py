from pathlib import Path
import os
class DependencyHandler:
    CUSTOM_MESSAGE_FOLDER='msg'
    SOURCE_FOLDER="src"
    CUSTOM_SERVICE_FOLDER="srv"
    INCLUDES_FOLDER="include"

    def __init__(self) -> None:
        self.package_flags={
            DependencyHandler.CUSTOM_MESSAGE_FOLDER:False,
            DependencyHandler.CUSTOM_SERVICE_FOLDER:False,
            DependencyHandler.INCLUDES_FOLDER:False,
            DependencyHandler.SOURCE_FOLDER:False
        }
    def get_custom_message_folder_flag(self) -> bool:
        return self.package_flags[DependencyHandler.CUSTOM_MESSAGE_FOLDER]

    def get_custom_service_folder_flag(self) -> bool:
        return self.package_flags[DependencyHandler.CUSTOM_SERVICE_FOLDER]

    def get_includes_folder_flag(self) -> bool:
        return self.package_flags[DependencyHandler.INCLUDES_FOLDER]

    def get_source_folder_flag(self) -> bool:
        return self.package_flags[DependencyHandler.SOURCE_FOLDER]
    #List of directories in package
    def setFlags(self,dirList:list):
        #Set flags
        for dir in dirList:
            try:
                self.package_flags[dir.stem]=True
            except:
                pass
    #Override in child classes
    def inferDependecies(self,package_directory:Path):
        NotImplementedError("This is an abstract method, please implement in a child class")
        return ""