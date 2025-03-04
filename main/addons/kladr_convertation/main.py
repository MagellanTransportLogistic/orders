import json
import uuid

from dbfpy3 import dbf


def read_dependencies():
    db = dbf.Dbf("KLADR\\ALTNAMES.DBF")
    keys = {}
    for r in db:
        keys[r['OLDCODE']] = r['NEWCODE']
    db.close()
    return keys


def read_levels():
    db = dbf.Dbf("KLADR\\SOCRBASE.DBF")
    keys = {}
    for r in db:
        k = {r['SCNAME']: {'level': r['LEVEL'], 'name': r['SOCRNAME']}}
        keys.update(k)
    db.close()
    return keys


def main():
    data = {'cities': [], 'raw': {}}
    data2 = {'cities': []}

    codes = read_dependencies()
    keys = read_levels()
    db = dbf.Dbf("KLADR\\KLADR.DBF")
    for row in db:
        abr = row['SOCR']
        keys_data_level = keys.get(abr, {})
        level = int(keys_data_level.get('level', 100))
        # if level in [1, 2, 3, 4]:
        if level > 0:
            code = row['CODE']
            if code[-2:] == '51':
                continue
            if code[-2:] == '00':
                subj = f'{code[:2]}00000000000'
                region = f'{code[0:][:5]}00000000'
                city = f'{code[0:][:8]}00000'
                point = f'{code[0:][:11]}00'
                name = f"{row['NAME']} {row['SOCR']}"

                data['raw'][code] = {
                    '_point': point,
                    '_city': city,
                    '_region': region,
                    '_subj': subj,
                    'name': name
                }

    iter_keys = ['_point', '_city', '_region', '_subj']

    for key in data['raw'].keys():
        for k in iter_keys:
            _name = data['raw'].get(data['raw'].get(key, {}).get(k), {}).get('name')
            if _name != data['raw'].get(key, {}).get('name'):
                data['raw'][key][k] = _name
            else:
                data['raw'][key][k] = ""

    for key in data['raw'].keys():
        _name = ''
        for k in iter_keys:
            text = data['raw'][key].get(k, '')
            if not text:
                continue
            if text not in _name:
                if _name == '':
                    _name = text
                else:
                    _name = f'{_name}, {text}'
        if len(_name) > 0:
            data['raw'][key]['full_name'] = data['raw'][key]['name'] + ', ' + _name
        # else:
        #     print(data['raw'][key])

        for k in iter_keys:
            data['raw'][key].pop(k)

    for _key in data['raw'].keys():
        _name = data['raw'][_key]['name']
        _full_name = data['raw'][_key].get('full_name', None)
        _uuid = str(uuid.uuid5(uuid.UUID('6e6281bb-2054-4d6e-a52d-d55d8fd04690'), f'{_key} {_name}'))
        if _full_name:
            data['cities'].append(
                {
                    'uuid': _uuid,
                    'code': _key,
                    'name': _name,
                    'full_name': _full_name
                }
            )
        else:
            if ' г' in data['raw'][_key]['name']:
                data2['cities'].append(
                    {
                        'uuid': _uuid,
                        'code': _key,
                        'name': data['raw'][_key]['name'],
                        'full_name': data['raw'][_key]['name'],
                    }
                )
    data.pop('raw')

    with open('locations.json', 'w', encoding='utf8') as f:
        f.write(json.dumps(data, indent=4, ensure_ascii=False))

    adding_country = [
        ('BL.txt', 'Белоруссия'),
        ('KZ.txt', 'Казахстан'),
        ('CN.txt', 'Китай'),
        ('AMR.txt', 'Армения'),
        ('TRK.txt', 'Турция'),
        ('LIT.txt', 'Литва'),
    ]
    for cnt in adding_country:
        with open(f'ADDINS\\{cnt[0]}', 'r', encoding='utf8') as f:
            _code = 1
            for line in f:
                if len(line.strip()) == 0:
                    continue
                _uuid = str(uuid.uuid5(uuid.UUID('6e6281bb-2054-4d6e-a52d-d55d8fd04690'), f'{line} {cnt[1]}'))
                data2['cities'].append(
                    {
                        'uuid': _uuid,
                        'code': _code,
                        'name': f'{line.rstrip().lstrip()}',
                        'full_name': f'{line.rstrip().lstrip()} г, {cnt[1]}'
                    })
                _code += 1

    with open('locations_add.json', 'w', encoding='utf8') as f:
        f.write(json.dumps(data2, indent=4, ensure_ascii=False))


main()
