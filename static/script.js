function createLine(container, x1, y1, x2, y2) {
    const ns = "http://www.w3.org/2000/svg";

    const line = document.createElementNS(ns, "line");
    line.setAttribute("x1", x1);
    line.setAttribute("y1", y1);
    line.setAttribute("x2", x2);
    line.setAttribute("y2", y2);
    line.setAttribute("stroke", "#4a90d9");
    line.setAttribute("stroke-width", "2");

    container.appendChild(line);
}

function getBounds(nodes) {
    const xs = nodes.map(n => n.x);
    const ys = nodes.map(n => n.y);
    return {
        minX: Math.min(...xs),
        maxX: Math.max(...xs),
        minY: Math.min(...ys),
        maxY: Math.max(...ys),
    };
}

function createScaler(bounds, containerWidth, containerHeight, padding = 50) {
    const graphWidth = bounds.maxX - bounds.minX || 1;
    const graphHeight = bounds.maxY - bounds.minY || 1;

    const scaleX = (containerWidth - padding * 2) / graphWidth;
    const scaleY = (containerHeight - padding * 2) / graphHeight;

    const scale = Math.min(scaleX, scaleY);

    const scaledWidth = graphWidth * scale;
    const scaledHeight = graphHeight * scale;

    const offsetX = (containerWidth - scaledWidth) / 2;
    const offsetY = (containerHeight - scaledHeight) / 2;

    function scalePoint(x, y) {
        return {
            x: offsetX + (x - bounds.minX) * scale,
            y: offsetY + (y - bounds.minY) * scale,
        };
    }

    scalePoint.factor = scale;

    return scalePoint;
}

function createNode(container, node, scale, radius = 10) {
    const ns = "http://www.w3.org/2000/svg";
    let point = scale(node.x, node.y);
    let label = node.name;

    const circle = document.createElementNS(ns, "circle");
    circle.setAttribute("cx", point.x);
    circle.setAttribute("cy", point.y);
    circle.setAttribute("r", radius);
    circle.setAttribute("fill", node.metadata.color);

    container.appendChild(circle);

    if (label !== undefined && label !== null) {
        const text = document.createElementNS(ns, "text");
        text.setAttribute("x", point.x);
        text.setAttribute("y", point.y - radius * 2 - 1);
        text.setAttribute("text-anchor", "middle");
        text.setAttribute("font-size", "10");
        text.setAttribute("fill", "#333");
        text.textContent = label;
        container.appendChild(text);
    }
}

async function generateGraph() {
    const maps_el = document.querySelector("#maps");
    const response = await fetch("/api/v1/simulation?path=" + maps_el.value);
    const container = document.querySelector('.container');
    container.innerHTML = "";

    let data = await response.json();
    let graph = data.graph;
    let nodes = graph.nodes;
    let edges = graph.edges;
    const bounds = getBounds(nodes);

    const scale = createScaler(bounds, container.clientWidth, container.clientHeight, 100);

    for (let i = 0; i < edges.length; i++) {
        let point1 = scale(edges[i].source.x, edges[i].source.y);
        let point2 = scale(edges[i].target.x, edges[i].target.y);

        createLine(container, point1.x, point1.y, point2.x, point2.y);
    }

    for (let i = 0; i < nodes.length; i++) {
        createNode(container, nodes[i], scale);
    }
}

function createOptionMap(map) {
    const opt = document.createElement("option");
    opt.textContent = map[0];
    opt.value = map[1];
    opt.classList.add("elMap");
    return opt;
}

async function createMapsChoose() {
    const response = await fetch("/api/v1/getMaps");
    let data = await response.json();
    const maps_el = document.querySelector("#maps");
    
    if (data.length == 0) {
        return null;
    }

    for (let i = 0; i < data.length; i++) {
        let opt = createOptionMap(data[i]);
        maps_el.appendChild(opt);
    }

    maps_el.addEventListener('change', (event) => generateGraph())
}

createMapsChoose();