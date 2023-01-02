import os
import sys
import json

index = 0
dataArr = []
dictNameId = {}

def visit(dir):
    arr = os.listdir(dir)
    for name in arr:
        path = os.path.join(dir, name)
        if os.path.isdir(path):
            visit(path)
        else:
            if name.endswith('.swift'):
                print('visit: ' + path)
                visitFile(path)


def visitFile(path):
    line = os.popen('sourcekitten structure --file ' + path).read()
    # print(line)
    try:
        dict = json.loads(line)
    except Exception as e:
        print('Exception in file ' + path)
        print(e)
        return

    for sub in dict['key.substructure']:
        kind = sub['key.kind']
        if kind == 'source.lang.swift.decl.class' or kind == 'source.lang.swift.decl.struct' or kind == 'source.lang.swift.decl.protocol' or kind == 'source.lang.swift.decl.enum':
            global index
            index += 1
            id = index
            data = {}
            name = sub['key.name']
            data['id'] = id
            data['name'] = name
            data['kind'] = kind.split('.')[-1]
            dataArr.append(data)
            dictNameId[name] = id
            # print('class: ' + name)
            if 'key.inheritedtypes' in sub: # class
                parents = []
                data['parents'] = parents
                protocols = []
                data['protocols'] = protocols
                i = 0
                for s in sub['key.inheritedtypes']:
                    i += 1
                    if i == 1:
                        parents.append(s['key.name'])
                    else:
                        protocols.append(s['key.name'])

            if 'key.substructure' in sub: # class members
                variables = []
                data['variables'] = variables
                temporaries = []
                data['temporaries'] = temporaries
                for s in sub['key.substructure']:
                    if s['key.kind'] == 'source.lang.swift.decl.var.instance':
                        if 'key.typename' in s:
                            variables.append(s['key.typename'])
                    if s['key.kind'] == 'source.lang.swift.expr.call':
                        variables.append(s['key.name'])
                    if s['key.kind'] == 'source.lang.swift.decl.function.method.instance':
                        if 'key.typename' in s: # return value
                                temporaries.append(s['key.typename'])
                        visitMethod(s, temporaries)


def visitMethod(sub, temporaries):
    if 'key.substructure' in sub:
        for s in sub['key.substructure']:
            if s['key.kind'] == 'source.lang.swift.decl.var.parameter':
                if 'key.typename' in s:
                    temporaries.append(s['key.typename'])
            if s['key.kind'] == 'source.lang.swift.decl.var.local':
                if 'key.typename' in s:
                    temporaries.append(s['key.typename'])
            if s['key.kind'] == 'source.lang.swift.expr.call':
                    temporaries.append(s['key.name'])
            visitMethod(s, temporaries)


def replaceName(type, data):
    ids = []
    if type in data:
        for name in data[type]:
            if name.endswith('?') or name.endswith('!'):
                name = name[:-1]
            if name in dictNameId:
                id = dictNameId[name]
                ids.append(id)
    data[type] = ids


if __name__ == '__main__':
    if len(sys.argv) < 2:
        visit('./')
    else:
        visit(sys.argv[1])
        
    for data in dataArr:
        replaceName('parents', data)
        replaceName('protocols', data)
        replaceName('variables', data)
        replaceName('temporaries', data)


    data = os.path.join(os.path.dirname(sys.argv[0]), 'data.json')
    f = open(data, 'w')
    f.write(json.dumps(dataArr))
    f.close()