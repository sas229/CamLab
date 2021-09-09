# import sys
# from ruamel.yaml import YAML

# yaml_str = """\
# first_name: Art
# occupation: Architect  # This is an occupation comment
# about: Art Vandelay is a fictional character that George invents...
# """

# yaml = YAML()
# data = yaml.load(yaml_str)
# data.insert(1, 'last name', 'Vandelay', comment="new key")
# # yaml.dump(data, "/test.yaml")

# with open("test.yaml", "w") as file:
#     yaml = YAML()
#     yaml.dump(data, file)

import sys
import copy
from ruamel.yaml import YAML

# data = {1:{1: [{1: 1, 2: 2}, {1: 1, 2: 2}], 2: 2}, 2: 42}
acquisition = [
    {"Channel": "AIN0", "Name": "Ch_1", "Unit": "V", "Slope": 1.0, "Offset": 0.00, "Log": False, "Autozero": True},
    {"Channel": "AIN1", "Name": "Ch_2", "Unit": "V", "Slope": 1.0, "Offset": 0.00, "Log": False, "Autozero": True},
    {"Channel": "AIN2", "Name": "Ch_3", "Unit": "V", "Slope": 1.0, "Offset": 0.00, "Log": False, "Autozero": True},
    {"Channel": "AIN3", "Name": "Ch_4", "Unit": "V", "Slope": 1.0, "Offset": 0.00, "Log": False, "Autozero": True},
    {"Channel": "AIN4", "Name": "Ch_5", "Unit": "V", "Slope": 1.0, "Offset": 0.00, "Log": False, "Autozero": True},
    {"Channel": "AIN5", "Name": "Ch_6", "Unit": "V", "Slope": 1.0, "Offset": 0.00, "Log": False, "Autozero": True},
    {"Channel": "AIN6", "Name": "Ch_7", "Unit": "V", "Slope": 1.0, "Offset": 0.00, "Log": False, "Autozero": True},
    {"Channel": "AIN7", "Name": "Ch_8", "Unit": "V", "Slope": 1.0, "Offset": 0.00, "Log": False, "Autozero": True},
]
acquisition2 = copy.deepcopy(acquisition)
print(type(acquisition2))

data = {}
data["global"] = {"darkMode": True, "controlRate": 1000.00, "acquisitionRate": 100.00, "averageSamples": 10, "path": "/data", "filename": "junk"}
data["devices"] = {"AMY": {"ID": 123456789, "Connection": 1, "Address": "N/A", "Acquisition": acquisition}}
# data["devices"] = {"AMY": {"ID": 123456789, "Connection": 1, "Address": "N/A", "Acquisition": acquisition},
#                     "BEN": {"ID": 123456789, "Connection": 1, "Address": "N/A", "Acquisition": acquisition2}}
data["devices"]["BEN"] = {"ID": 123456789, "Connection": 1, "Address": "N/A", "Acquisition": acquisition2}


yaml = YAML()
yaml.explicit_start = True
yaml.dump(data, sys.stdout)
yaml.indent(sequence=4, offset=2)
yaml.dump(data, sys.stdout)

with open("test.yaml", "w") as file:
    yaml = YAML()
    yaml.dump(data, file)

with open("test.yaml", "r") as file:
    data = yaml.load(file) 

print(data["devices"]["AMY"]["Acquisition"][0])
print(data["devices"]["AMY"]["Acquisition"][1])

# print(data)

# def sequence_indent_four(s):
#     # this will fail on direclty nested lists: {1; [[2, 3], 4]}
#     levels = []
#     ret_val = ''
#     for line in s.splitlines(True):
#         ls = line.lstrip()
#         indent = len(line) - len(ls)
#         if ls.startswith('- '):
#             if not levels or indent > levels[-1]:
#                 levels.append(indent)
#             elif levels:
#                 if indent < levels[-1]:
#                     levels = levels[:-1]
#             # same -> do nothing
#         else:
#             if levels:
#                 if indent <= levels[-1]:
#                     while levels and indent <= levels[-1]:
#                         levels = levels[:-1]
#         ret_val += '  ' * len(levels) + line
#     return ret_val

# yaml = YAML()
# yaml.explicit_start = True
# yaml.dump(data, sys.stdout, transform=sequence_indent_four)