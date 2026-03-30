import json, re

with open('cries_children.json') as f:
    cries = json.load(f)
with open('wwise_query_output.json') as f:
    switches = json.load(f)

switch_by_num = {}
for s in switches:
    name = s['name']
    m = re.search(r'(\d+)$', name)
    if m:
        switch_by_num[int(m.group(1))] = name

BS = '\\'
assignments = []
for cry in cries:
    name = cry['name']
    num = int(name.split('_')[0])
    sw_name = switch_by_num[num]
    child_path = f"{BS}Actor-Mixer Hierarchy{BS}Default Work Unit{BS}SFX{BS}SFX_Pokemon_Cries{BS}{name}"
    sw_path = f"{BS}Switches{BS}Default Work Unit{BS}PokemonID{BS}{sw_name}"
    assignments.append({'child': child_path, 'state_or_switch': sw_path})

print(f'Total assignments: {len(assignments)}')

batch_size = 51
for i in range(0, len(assignments), batch_size):
    batch = assignments[i:i+batch_size]
    fname = f'cry_batch{i // batch_size}.json'
    with open(fname, 'w') as f:
        json.dump(batch, f)
    print(f'Batch {i // batch_size}: {len(batch)} assignments')
