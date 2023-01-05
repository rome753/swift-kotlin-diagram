main();

function main() {
    readTextFile('generate/data.json');
}

function readTextFile(file) {
    var rawFile = new XMLHttpRequest();
    rawFile.open("GET", file, false);
    rawFile.onreadystatechange = function ()
    {
        if(rawFile.readyState === 4)
        {
            if(rawFile.status === 200 || rawFile.status == 0)
            {
                var allText = rawFile.responseText;
                handleJsonStr(allText);
            }
        }
    }
    rawFile.send(null);
}

function handleJsonStr(str) {
    var dataArr = JSON.parse(str);

    var nodeArr = []
    var edgeArr = []

    var nodeTypes = ['class','struct','protocol','enum']
    var edgeTypes = ['parents','protocols','variables','temporaries']

    for (var data of dataArr) {
        var node = createNode(data['id'], data['name'], data['kind'])
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
        return true;
    };

    const edgesFilter = (edge) => {
        return edge.type != 'temporaries' || temporariesEnabled;
    };

    const nodesView = new vis.DataView(nodes, { filter: nodesFilter });
    const edgesView = new vis.DataView(edges, { filter: edgesFilter });

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

function createNode(id, label, type) {
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