import re


def save_note(note):
    with open(f'{note['name'].rstrip()}.md', 'w') as file:
        file.write('---\n')
        file.write('appearance: >\n')
        if 'appearance' in note:
            file.write(note['appearance'] + '\n')
        file.write('roleplaying:\n')
        if 'roleplaying' in note:
            for i in note['roleplaying']:
                file.write(f'  - {i.rstrip()}\n')
        file.write('background: |\n')
        if 'background' in note:
            file.write(f'  {note["background"]}\n')
        file.write('---')


with open('exported_from_notes.txt', 'r') as file:
    text_lines = file.readlines()

note = None
key = None
value = None
for line in text_lines:
    print(line)
    m = re.match(r'^$', line)
    if (m is not None):
        continue
    m = re.match(r'^<!-- ### Start Note ### -->$', line)
    if (m is not None):
        if (key is not None) and (value is not None):
            note[key] = value
            save_note(note)
        note = {}
        key = 'name'
        value = ''
        continue
    m = re.match(r'^(\w*):$', line)
    if (m is not None):
        new_key = m.group(1).lower()
        if new_key == 'backstory':
            new_key = 'background'
        if new_key in ['roleplaying', 'background', 'appearance']:
            if key is not None:
                note[key] = value
            key = new_key
            if (key == 'roleplaying'):
                value = []
            else:
                value = ''
            continue
    if (key == 'roleplaying'):
        value.append(line)
    else:
        value = value + line
if (key is not None) and (value is not None):
    note[key] = value
save_note(note)
