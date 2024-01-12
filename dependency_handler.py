from pathlib import Path
import os
import re
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
    #Get included files, assumes cpp or hpp file
    def get_includes(self, file_path: Path):
        # Regex that matches includes
        include_pattern = re.compile(r'^\s*#include\s*["](.+)["]\s*$')
        includes = set()
        print(file_path)
        with open(file_path, 'r') as file:
            for line in file:
                match = include_pattern.match(line)
                if match:
                    includes.add(match.group(1))
        return includes
    
    #recursively iterate through directories to get includes
    def getSourceDependencies(self, directory: Path):
        included_packages = set()
        for x in directory.iterdir():
            if x.is_dir():
                included_packages=included_packages.union(self.getSourceDependencies(x)) 
            else:
                includes = self.get_includes(x.resolve())
                included_packages = included_packages.union(includes)
        return included_packages
    
    #Removes includes that are not a package in the workspace or in ROS
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
            isROSPKG = (Path(f'/opt/ros/{self.ros_version}/share') / cand).exists()
            isLocalPKG = (parent_directory / cand).exists()
            
            if isLocalPKG or isROSPKG:
                shared_directories.add(cand)

        return shared_directories
    #This can be shared
    def inferSourceDependencies(self, package_directory: Path): 
        #Get directories in package
        directories = [x for x in package_directory.iterdir() if x.is_dir()]

        #Check if it contains some important directories
        self.setFlags(directories)

        # These dependencies are deduced from the code
        src_dependencies = set()
        if self.get_includes_folder_flag():
            #Ros packages should follow this structure, not my choice
            includePath = package_directory / "include" / package_directory.stem
            #Verify it is formatted properly
            assert includePath.exists(), 'Include path is not formatted properly, directory should be of form include/package_name/files.extension'
            src_dependencies = src_dependencies.union(self.getSourceDependencies(includePath))

        #Get dependencies in source
        if self.get_source_folder_flag():
            src_dependencies = src_dependencies.union(self.getSourceDependencies(package_directory/'src'))

        #Clean up includes that may be standard c++ includes, we only care about packages in our workspace or in ROS
        package_dependencies = self.purgeNonPackages(package_directory.resolve(), src_dependencies)
        return package_dependencies