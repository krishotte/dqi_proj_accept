from os import path
import re


template_file = path.join(path.join(path.split(path.realpath(__file__))[0], 'input'), 'protokol2b.txt')
print('template file: ', template_file)

with open(template_file, encoding='utf-8') as f:
    template_all = f.read()

lines = template_all.split('\n')

darkred = [118/255, 22/255, 22/255, 1]
darkgreen = [ 32/255, 64/255, 16/255, 1]
black = [0, 0, 0, 1]


def get_data():
    loaded_data = []
    id_p = re.compile('[0-9]\.{0,1}[0-9]{0,2}\.{0,1}[0-9]{0,2}\.{0,1}')
    i = 0
    for line in lines:
        # print(line)
        id_m = id_p.search(line)
        try:
            id1 = id_m.group()
        except AttributeError:
            id1 = 'not found'
        
        print('id found: ', id1)
        name1 = line.split(':')[0]
        name2 = name1[len(id1)+1:len(name1)]
        print('name: ', name2)
        try:
            flags = line.split(':')[1]
            print('flags: ', flags)
            flags = 1
        except IndexError:
            print('flags none')
            flags = None

        # TODO: vcls selection based on flags, not id1 length

        if len(id1) < 6:
            vcls = 'ItemSectionTitle'
        else:
            vcls = 'ItemBasicNA'
        single_data = {
            'id1': id1,
            'name1': name2,
            'flag1': flags,
            'viewclass': vcls,  # 'Item3'
            'status_color': black,
            'status': '--',
            'note': '--',
        }
        loaded_data.append(single_data)
    return loaded_data


if __name__ == '__main__':
    data = get_data()
    for each in data:
        print(each)
