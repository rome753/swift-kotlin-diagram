
const hideDirs = {}
const hideFiles = {}
var nodesView = undefined
var edgesView = undefined

main();

function main() {
    readTextFile('generate/data.json');
    readTextFile('generate/tree.json');
}

function readTextFile(path) {
    var rawFile = new XMLHttpRequest();
    rawFile.open("GET", path, false);
    rawFile.onreadystatechange = function ()
    {
        if(rawFile.readyState === 4)
        {
            if(rawFile.status === 200 || rawFile.status == 0)
            {
                var allText = rawFile.responseText;
                handleJsonStr(path, allText);
            }
        }
    }
    rawFile.send(null);
}

function handleJsonStr(path, str) {
    let json = JSON.parse(str);
    if (path == 'generate/data.json') {
        handleDataJson(json)
    } else if (path == 'generate/tree.json') {
        handleTreeJson(json)
    }
}

function handleTreeJson(obj) {
    var tree = document.getElementById("mytree");
    var html = generateTree(obj)
    tree.innerHTML = '<ul>' + html + '</ul>'

    for (var ele of document.querySelectorAll('#file')) {
        // console.log(li.innerHTML)
        ele.addEventListener('click', function(e) {
            var file = e.target.innerHTML
            console.log(file)
            if (hideFiles[file] == true) {
                hideFiles[file] = false
                e.target.style.opacity = 1
            } else {
                hideFiles[file] = true
                e.target.style.opacity = 0.3
            }
            nodesView.refresh()
        });
    }

    for (var ele of document.querySelectorAll('#dir')) {
        // console.log(li.getElementsByClassName('li'))
        ele.addEventListener('click', function(e) {
            var div = e.target
            var hide = div.style.opacity != 0.3
            div.style.opacity = hide ? 0.3 : 1
            
            var ul = div.nextElementSibling
            var child = ul.firstElementChild
            while (child != ul.lastElementChild) {
                hideListItemOrNot(child, hide)
                child = child.nextElementSibling
            }        
            hideListItemOrNot(child, hide)        
            nodesView.refresh()
        });
    }
}

function hideListItemOrNot(li, hide) {
    var div = li.firstElementChild
    if (div.id == 'file') {
        hideFiles[div.innerHTML] = hide
        div.style.opacity = hide ? 0.3 : 1
    }
}

function generateTree(obj) {
    if (typeof obj == 'string') {
        return `<div id='file'>${obj}</div>`
    } else {
        var str = `<div id='dir'>${obj['name']}</div><ul>`
        for (var o of obj['list']) {
            str += '<li>' + generateTree(o) + '</li>'
        }
        return str + '</ul>'
    }
}

function handleDataJson(dataArr) {
    var nodeArr = []
    var edgeArr = []

    var nodeTypes = ['class','struct','protocol','enum']
    var edgeTypes = ['parents','protocols','variables','temporaries']

    for (var data of dataArr) {
        var node = createNode(data['id'], data['name'], data['kind'], data['file'])
        nodeArr.push(node)
        
        var from = data['id']
        for (var type of edgeTypes) {
            for (var to of data[type]) {
                var edge = createEdge(from, to, type)
                edgeArr.push(edge)
            }
        }
    }
    
    var temporariesEnabled = true

    let nodes = new vis.DataSet(nodeArr)
    let edges = new vis.DataSet(edgeArr)

    const nodesFilter = (node) => {
        if (hideFiles[node.file] == true) {
            return false
        }
        return true;
    };

    const edgesFilter = (edge) => {
        return edge.type != 'temporaries' || temporariesEnabled;
    };

    nodesView = new vis.DataView(nodes, { filter: nodesFilter });
    edgesView = new vis.DataView(edges, { filter: edgesFilter });

    const edgeFilters = document.getElementsByName("edgesFilter");
    edgeFilters.forEach((filter) =>
        filter.addEventListener("change", (e) => {
        const { value, checked } = e.target;
        temporariesEnabled = checked;
        edgesView.refresh();
        })
    );

    // create a network
    var container = document.getElementById("mynetwork");
    var data = {
    nodes: nodesView,
    edges: edgesView,
    };
    var options = {
        physics: {
          enabled: true,
        },
        // layout: {
        //     hierarchical: {
        //       direction: 'Up-Down',
        //     },
        // },
    };
    var network = new vis.Network(container, data, options);
}

function createNode(id, label, type, file) {
    var shape = 'box'
    var dashes = false
    switch(type) {
        case 'class':
            break
        case 'struct':
            shape = 'ellipse'
            break
        case 'protocol':
            dashes = true
            break
        case 'enum':
            shape = 'dot'
            break
    }
    return {
        file: file,
        id: id,
        label: label,
        shape: shape,
        shapeProperties: dashes ? { borderDashes: [5, 5] } : {},
        // color: { background: "transparent"},
    }
}

function createEdge(from, to, type) {
    var arrowType = 'triangle'
    var dashes = false
    switch(type) {
        case 'parents':
            break
        case 'protocols':
            dashes = true
            break
        case 'variables':
            arrowType = 'vee'
            break
        case 'temporaries':
            arrowType = 'vee'
            dashes = true
            break
    }
    return {
        type: type,
        from: from,
        to: to,          
        arrows: {
            to: {
                enabled: true,
                type: arrowType,
            },
        },
        dashes: dashes,
        smooth: { 
            enabled: true,
            type: 'discrete',
        },
        physics: false,
    }
}