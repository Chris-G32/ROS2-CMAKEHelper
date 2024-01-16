from pathlib import Path
import re



#Removes includes that are not a package in the workspace or in ROS
def purge_non_packages(package_directory: Path, includes: set,ros_version):
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
        isROSPKG = (Path(f'/opt/ros/{ros_version}/share') / cand).exists()
        isLocalPKG = (parent_directory / cand).exists()
        
        if isLocalPKG or isROSPKG:
            shared_directories.add(cand)

    return shared_directories

#Get included files, assumes cpp or hpp file
def get_includes(file_path: Path):
    # Regex that matches includes
    include_pattern = re.compile(r'^\s*#include\s*["](.+)["]\s*$')
    includes = set()
    with open(file_path, 'r') as file:
        for line in file:
            match = include_pattern.match(line)
            if match:
                includes.add(match.group(1))
    return includes

#Get dependencies for a file
def get_file_dependencies(package_directory:Path,file_path:Path,ros_version='humble'):
    includes=get_includes(file_path)
    dependencies=purge_non_packages(package_directory,includes,ros_version)
    return dependencies

def deduce_is_executable(file_path:Path):
    cpp_main_declaration_pattern = re.compile(r'\bint\s*main\b')
    with open(file_path, 'r') as file:
        for line in file:
            match = cpp_main_declaration_pattern.match(line)
            if match:
                return True
    return False


def traverse_directory(directory:Path,callback):
    for x in directory.iterdir():
        if x.is_dir():
            traverse_directory(x,callback)
        else:
            callback(x)



def generate_cmake(package_directory:Path):
    executables=set()
    dependency_map={}
    def file_callback(file:Path):
        is_executable=deduce_is_executable(file)
        if is_executable:
            executables.add(file)
            dependency_map[file]=get_file_dependencies(package_directory,file)
        else:
            # print(f'{file} Not executable')
            pass

    traverse_directory(package_directory,file_callback)
    # print(executables)
    print(dependency_map)


if __name__=="__main__":
    package=Path('/home/chris/TeleBot-4R/src/motion')
    file=Path('/home/chris/TeleBot-4R/src/motion/include/motion/driver.hpp')
    # print(deduce_is_executable(Path('test_file.cpp')))
    # print(get_file_dependencies(package,file))
    generate_cmake(package)