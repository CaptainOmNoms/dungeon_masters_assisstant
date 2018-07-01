import json


file = open('monster_data.json')
json_string = file.read()

actions = list()
special = list()
legendary = list()

for i in range(0, 325):
    data = json.loads(json_string)[i]
    if 'special_abilities' in data.keys():
        for value in data['special_abilities']:
            for key in value.keys():
                if key not in special:
                    special.append(key)

    if 'actions' in data.keys():
        for value in data['actions']:
            for key in value.keys():
                if key not in actions:
                    actions.append(key)

    if 'legendary_actions' in data.keys():
        for value in data['legendary_actions']:
            for key in value.keys():
                if key not in legendary:
                    legendary.append(key)

print('actions')
print('\t', *actions, sep='\n\t')

print('\n\nspecial')
print('\t', *special, sep='\n\t')

print('\n\nlegendary')
print('\t', *legendary, sep='\n\t')



