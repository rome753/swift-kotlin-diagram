import os
import sys
import json

index = 0
dataArr = []
dictNameId = {}

def visit(path):
    if os.path.isdir(path):
        arr = os.listdir(path)
        ret = []
        for name in arr:
            p = os.path.join(path, name)
            r = visit(p)
            if r is not None:
                ret.append(r)
        return {os.path.basename(path): ret}
    else:
        if path.endswith('.swift'):
            print('visit: ' + path)
            visitFile(path)
            return os.path.basename(path)
        return None


def visitFile(path):
    structure = os.popen('sourcekitten structure --file ' + path).read()
    # print(structure)
    try:
        dict = json.loads(structure)
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
            data['file'] = os.path.basename(path)
            data['name'] = name
            data['kind'] = kind.split('.')[-1]
            dataArr.append(data)
            dictNameId[name] = id

            parents = []
            data['parents'] = parents
            protocols = []
            data['protocols'] = protocols
            variables = []
            data['variables'] = variables
            temporaries = []
            data['temporaries'] = temporaries

            print('\tvisit: ' + name)
            if 'key.inheritedtypes' in sub: # ParentClass and protocols
                i = 0
                for s in sub['key.inheritedtypes']:
                    i += 1
                    name = s['key.name'] # ParentClass
                    if i == 1:
                        j = name.find('<') # ParentClass<T1, T2>
                        if j != -1:
                            arr = name[j+1:-1].split(', ')
                            for a in arr:
                                variables.append(a)
                            name = name[:j]
                        parents.append(name)
                    else:
                        protocols.append(s['key.name'])

            if 'key.substructure' in sub: # class members
                for s in sub['key.substructure']:
                    if s['key.kind'] == 'source.lang.swift.decl.var.instance':
                        if 'key.typename' in s:
                            variables.append(s['key.typename'])
                    if s['key.kind'] == 'source.lang.swift.expr.call':
                        name = s['key.name']
                        i = name.find('.')
                        if i != -1: # MyClass.staticFunc
                            name = name[:i]
                        variables.append(name)
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
                    name = s['key.name']
                    i = name.find('.')
                    if i != -1: # MyClass.staticFunc
                        name = name[:i]
                    temporaries.append(name)
            visitMethod(s, temporaries)


def replaceName(type, data):
    ids = []
    if type in data:
        for name in data[type]:
            if name.endswith('?') or name.endswith('!'): # optional
                name = name[:-1]
            if name in dictNameId:
                id = dictNameId[name]
                ids.append(id)
    data[type] = ids


if __name__ == '__main__':
    argc = len(sys.argv)
    if argc < 2:
        visit('.')
    else:
        tree = visit(sys.argv[1])
        data = os.path.join(os.path.dirname(sys.argv[0]), 'generate', 'tree.json')
        f = open(data, 'w')
        f.write(json.dumps(tree))
        f.close()
        
    for data in dataArr:
        replaceName('parents', data)
        replaceName('protocols', data)
        replaceName('variables', data)
        replaceName('temporaries', data)


    data = os.path.join(os.path.dirname(sys.argv[0]), 'generate', 'data.json')
    f = open(data, 'w')
    f.write(json.dumps(dataArr))
    f.close()