import os
import re
import codecs

def document(S, properties):
    d = {}
    values = S.split('\t')
##    print(properties)
    for i in range(len(values)):
##        print(len(properties))
##        print(len(values))
        #print(values)
        if '&' in values[i]:
            d[properties[i].strip()] = values[i].replace("'", '').replace('"', '').split('& ')
        else:
            d[properties[i].strip()] = values[i].replace("'", '').replace('"', '')
    return d

def input(filename):
    arr = open(filename + '.txt', 'r', encoding='utf-8').read().split('\n')
    properties = arr[0].replace('\ufeff', '').split('\t')
    lines = []
    for line in arr[1:]:
       #print(line)
       lines.append(str(document(line, properties)).replace("'", '"'))
    return lines

def create_files(filename):
    lines = input(filename)
    if not os.path.exists(filename):
            os.makedirs(filename)
    i = 1
    for line in lines:
##        print(line)
        a = open('./' + filename + '/' + str(i) + '.json', 'w', encoding='utf-8')
        line = line.replace('"": "",',"")
        line = line.replace(',"": ""',"")
        line = line.replace('\\xa0',' ')
##        line = re.sub('""(?=[^,}])', '"', line, flags=re.U)
##        line = line.replace('""', '"').replace(': ",', ': "",')
        a.write(line)
        a.close()
        i += 1


create_files('sry')
#create_files('verb+noun')
#create_files('noun+noun')
#create_files('adjective+noun')
