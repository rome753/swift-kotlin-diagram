import os
import sys
import json
import webbrowser

openBrowser = False

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
        if path.endswith('.kt'):
            print('visit: ' + path)
            return os.path.basename(path)
        return None


if __name__ == '__main__':
    argc = len(sys.argv)
    print('argv0 ' + sys.argv[0])
    runPath = ''
    projPath = ''
    if argc < 2:
        runPath = os.path.dirname(sys.argv[0])
        projPath = os.path.join(runPath, 'test')
    else:
        print('argv1 ' + sys.argv[1])
        openBrowser = True
        runPath = '.'
        projPath = sys.argv[1]
        
    os.chdir(os.path.join(runPath, 'kotlin'))

    tree = visit(projPath)
    data = os.path.join('..', 'generate', 'tree.json')
    f = open(data, 'w')
    f.write(json.dumps(tree))
    f.close()
        
    os.system('kotlinc myprocessor -cp symbol-processing-api-1.8.0-1.0.8.jar -d myprocessor.jar')
    os.system('jar uvMf myprocessor.jar META-INF')

    KSP_PLUGIN_OPT = 'plugin:com.google.devtools.ksp.symbol-processing'
    KSP_PLUGIN_JAR = 'symbol-processing-cmdline-1.8.0-1.0.8.jar'
    KSP_API_JAR = 'symbol-processing-api-1.8.0-1.0.8.jar'
    AP = 'myprocessor.jar'
    cmd = ('kotlinc '
    '-Xplugin=' + KSP_PLUGIN_JAR + ' '
    '-Xplugin=' + KSP_API_JAR + ' '
    '-Xallow-no-source-files '
    '-P plugin:com.google.devtools.ksp.symbol-processing:apclasspath=' + AP + ' '
    '-P plugin:com.google.devtools.ksp.symbol-processing:projectBaseDir=' + projPath + ' '
    '-P plugin:com.google.devtools.ksp.symbol-processing:incremental=false '
    '-P plugin:com.google.devtools.ksp.symbol-processing:classOutputDir=../generate '
    '-P plugin:com.google.devtools.ksp.symbol-processing:javaOutputDir=../generate '
    '-P plugin:com.google.devtools.ksp.symbol-processing:kotlinOutputDir=../generate '
    '-P plugin:com.google.devtools.ksp.symbol-processing:resourceOutputDir=../generate '
    '-P plugin:com.google.devtools.ksp.symbol-processing:kspOutputDir=../generate '
    '-P plugin:com.google.devtools.ksp.symbol-processing:cachesDir=../generate '
    '' + projPath)
    os.system(cmd)