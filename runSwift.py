import os
import sys
import json
import webbrowser

openBrowser = False
printStructrue = False

index = 0
dataArr = []

def visit(path):
    if os.path.isdir(path):
        arr = os.listdir(path)
        ret = []
        for name in arr:
            p = os.path.join(path, name)
            r = visit(p)
            if r is not None:
                ret.append(r)
        return {
            'name': os.path.basename(path),
            'list': ret
        }
    else:
        if path.endswith('.swift'):
            print('visit: ' + path)
            visitFile(path)
            return os.path.basename(path)
        return None


def visitFile(path):
    structure = os.popen('sourcekitten structure --file ' + path).read()
    if printStructrue:
        print(structure)
    try:
        dict = json.loads(structure)
    except Exception as e:
        print('Exception in file ' + path)
        print(e)
        return

    for sub in dict['key.substructure']:
        kind = sub['key.kind']
        validKinds = ['source.lang.swift.decl.class', 'source.lang.swift.decl.struct', 'source.lang.swift.decl.protocol', 'source.lang.swift.decl.enum']
        if kind not in validKinds:
            continue
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

        parents = []
        data['parents'] = parents
        protocols = []
        data['protocols'] = protocols
        variables = []
        data['variables'] = variables
        temporaries = []
        data['temporaries'] = temporaries

        varDetails = []
        funcDetails = []

        print('-visit: ' + name)
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
                if s['key.kind'].startswith('source.lang.swift.decl.var'): # .instance/.static/.class
                    type = s['key.kind'].split('.')[-1]
                    type = type if type != 'instance' else ''
                    typename = '' if 'key.typename' not in s else s['key.typename']
                    if typename != '':
                        if type == '':
                            variables.append(typename)
                        else:
                            temporaries.append(typename)
                    s1 = '' if typename == '' else ': ' + typename
                    s2 = '' if type == '' else ' (' + type + ')'
                    varDetails.append('- ' + s['key.name'] + s1 + s2)
                if s['key.kind'] == 'source.lang.swift.expr.call':
                    name = s['key.name']
                    i = name.find('.')
                    if i != -1: # MyClass.staticFunc
                        name = name[:i]
                    variables.append(name)
                if s['key.kind'].startswith('source.lang.swift.decl.function.method'): # .instance/.static/.class
                    type = s['key.kind'].split('.')[-1]
                    type = type if type != 'instance' else ''
                    typename = '' if 'key.typename' not in s else s['key.typename']
                    if typename != '':
                        temporaries.append(typename)
                    
                    s1 = '' if typename == '' else ': ' + typename
                    s2 = '' if type == '' else ' (' + type + ')'
                    funcDetails.append('+ ' + s['key.name'] + s1 + s2)
                    visitMethod(s, temporaries)
                if s['key.kind'] == 'source.lang.swift.decl.enumcase':
                    varDetails.append('.' + s['key.substructure'][0]['key.name'])

        
        s1 = '\n'.join(varDetails)
        s2 = '\n'.join(funcDetails)
        data['detail'] = '\n-------------------------\n'.join([data['name'], s1, s2])


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
    data1 = []
    if type in data:
        for name in data[type]:
            if name.endswith('?') or name.endswith('!'): # optional
                name = name[:-1]
            data1.append(name)
    data[type] = data1


if __name__ == '__main__':
    argc = len(sys.argv)
    projPath = ''
    if argc < 2:
        printStructrue = True
        projPath = 'test'
    else:
        openBrowser = True
        projPath = sys.argv[1]

    tree = visit(projPath)
    genDir = os.path.join(os.path.dirname(sys.argv[0]), 'generate')
    if os.path.exists(genDir) == False:
        os.mkdir(genDir)
    data = os.path.join(genDir, 'tree.json')
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

    if openBrowser:
        webbrowser.open('http://localhost:8080/diagram.html')
        os.system('python3 -m http.server 8080')