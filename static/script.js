// ===================== Геометрия / отрисовка графа =====================

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

function estimateTextWidth(text, fontSize) {
    return text.length * fontSize * 0.6;
}

function planLabels(nodes, scale, baseFontSize = 10, minGap = 4) {
    const scaledNodes = nodes.map(n => {
        const p = scale(n.x, n.y);
        return { node: n, x: p.x, y: p.y };
    });

    const rows = [];
    const used = new Set();
    for (let i = 0; i < scaledNodes.length; i++) {
        if (used.has(i)) continue;
        const row = [scaledNodes[i]];
        used.add(i);
        for (let j = i + 1; j < scaledNodes.length; j++) {
            if (used.has(j)) continue;
            if (Math.abs(scaledNodes[j].y - scaledNodes[i].y) < 5) {
                row.push(scaledNodes[j]);
                used.add(j);
            }
        }
        row.sort((a, b) => a.x - b.x);
        rows.push(row);
    }

    const plan = new Map();

    for (const row of rows) {
        for (let i = 0; i < row.length; i++) {
            const label = row[i].node.name || "";
            const prevGap = i > 0 ? row[i].x - row[i - 1].x : Infinity;
            const nextGap = i < row.length - 1 ? row[i + 1].x - row[i].x : Infinity;
            const availableGap = Math.min(prevGap, nextGap);

            let fontSize = baseFontSize;
            let textWidth = estimateTextWidth(label, fontSize);

            while (textWidth > availableGap - minGap && fontSize > 6) {
                fontSize -= 1;
                textWidth = estimateTextWidth(label, fontSize);
            }

            const side = i % 2 === 0 ? "top" : "bottom";

            plan.set(row[i].node, { fontSize, side });
        }
    }

    return plan;
}

function createNode(container, node, scale, labelPlan, radius = 10) {
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
        const { fontSize, side } = labelPlan.get(node) || { fontSize: 10, side: "top" };
        const text = document.createElementNS(ns, "text");
        text.setAttribute("x", point.x);
        text.setAttribute(
            "y",
            side === "top"
                ? point.y - radius * 2 - 1
                : point.y + radius * 2 + fontSize
        );
        text.setAttribute("text-anchor", "middle");
        text.setAttribute("font-size", fontSize);
        text.setAttribute("fill", "#333");
        text.textContent = label;
        container.appendChild(text);
    }
}

// ===================== Состояние графа (кэш для анимации дронов) =====================

let nodeByName = new Map();
// ключ "sourceName_targetName" -> { source: nodeObj, target: nodeObj }
let edgeByConnectionName = new Map();
let currentScale = null;
let currentPlayback = null; // { stop() } — активная анимация, чтобы можно было остановить при смене карты

// ===================== Определение позиции дрона по тику =====================

function resolveDronePosition(drone, scale) {
    // Дрон стоит в узле
    if (drone.node_name) {
        const node = nodeByName.get(drone.node_name);
        if (!node) return null;
        return scale(node.x, node.y);
    }

    // Дрон "завис" на ребре (например, ждёт слот в restricted-зоне).
    // Явного прогресса вдоль ребра API не даёт, поэтому рисуем дрона
    // в середине ребра — при последовательных тиках на одном и том же
    // connection_name дрон просто визуально останется в этой точке,
    // что само по себе читается как "ожидание в очереди".
    if (drone.connection_name) {
        const edge = edgeByConnectionName.get(drone.connection_name);
        if (!edge) return null;
        const p1 = scale(edge.source.x, edge.source.y);
        const p2 = scale(edge.target.x, edge.target.y);
        return { x: (p1.x + p2.x) / 2, y: (p1.y + p2.y) / 2 };
    }

    return null;
}

// ===================== Анимация дронов по history =====================

function playHistory(history, dronesLayer, scale, tickDuration = 700) {
    const ns = "http://www.w3.org/2000/svg";
    const droneEls = new Map();

    function getOrCreateDrone(id) {
        if (droneEls.has(id)) return droneEls.get(id);
        const c = document.createElementNS(ns, "circle");
        c.setAttribute("r", 5);
        c.setAttribute("fill", "#e94b3c");
        c.setAttribute("stroke", "#ffffff");
        c.setAttribute("stroke-width", "1.5");
        c.style.transition =
            `cx ${tickDuration * 0.9}ms linear, ` +
            `cy ${tickDuration * 0.9}ms linear, ` +
            `opacity 0.3s ease`;
        dronesLayer.appendChild(c);
        droneEls.set(id, c);
        return c;
    }

    let tickIndex = 0;
    let playing = true;
    let timeoutId = null;

    function runTick() {
        if (!playing || tickIndex >= history.length) return;
        const tick = history[tickIndex];

        for (const drone of tick.drones) {
            const circle = getOrCreateDrone(drone.drone_id);
            const pos = resolveDronePosition(drone, scale);
            if (!pos) continue;

            circle.setAttribute("cx", pos.x);
            circle.setAttribute("cy", pos.y);
            circle.style.opacity = drone.is_finished ? "0.25" : "1";
        }

        tickIndex++;
        if (tickIndex < history.length) {
            timeoutId = setTimeout(runTick, tickDuration);
        }
    }

    runTick();

    return {
        stop() {
            playing = false;
            if (timeoutId) clearTimeout(timeoutId);
        },
    };
}

// ===================== Основной сценарий: загрузка + статичный граф + анимация =====================

async function generateGraph() {
    // если предыдущая анимация ещё играет — останавливаем её перед перерисовкой
    if (currentPlayback) {
        currentPlayback.stop();
        currentPlayback = null;
    }

    const maps_el = document.querySelector("#maps");
    const response = await fetch("http://127.0.0.1:8000" + "/api/v1/simulation?path=" + maps_el.value);
    const container = document.querySelector('.container');
    container.innerHTML = "";

    let data = await response.json();
    let graph = data.graph;
    let nodes = graph.nodes;
    let edges = graph.edges;
    const bounds = getBounds(nodes);

    const scale = createScaler(bounds, container.clientWidth, container.clientHeight, 100);
    currentScale = scale;

    nodeByName.clear();
    edgeByConnectionName.clear();
    nodes.forEach(n => nodeByName.set(n.name, n));

    // Рёбра рисуются один раз — статично, без анимации.
    for (let i = 0; i < edges.length; i++) {
        const e = edges[i];
        let point1 = scale(e.source.x, e.source.y);
        let point2 = scale(e.target.x, e.target.y);

        createLine(container, point1.x, point1.y, point2.x, point2.y);

        // индексируем connection_name в обе стороны — на случай, если
        // симулятор допускает проход по ребру в направлении target -> source
        edgeByConnectionName.set(`${e.source.name}_${e.target.name}`, { source: e.source, target: e.target });
        edgeByConnectionName.set(`${e.target.name}_${e.source.name}`, { source: e.target, target: e.source });
    }

    const labelPlan = planLabels(nodes, scale);

    for (let i = 0; i < nodes.length; i++) {
        createNode(container, nodes[i], scale, labelPlan);
    }

    // Отдельный слой поверх статичного графа — сюда рисуются только дроны.
    const ns = "http://www.w3.org/2000/svg";
    const dronesLayer = document.createElementNS(ns, "g");
    dronesLayer.setAttribute("class", "drones-layer");
    container.appendChild(dronesLayer);

    if (Array.isArray(data.history) && data.history.length > 0) {
        currentPlayback = playHistory(data.history, dronesLayer, scale);
    }
}

// ===================== Выбор карты =====================

function createOptionMap(map) {
    const optGroup = document.createElement("optgroup");
    optGroup.label = map[0].group;

    for (let i = 0; i < map.length; i++) {
        const opt = document.createElement("option");
        opt.textContent = map[i].name;
        opt.value = map[i].path;
        opt.classList.add("elMap");
        optGroup.appendChild(opt);
    }
    return optGroup;
}

async function createMapsChoose() {
    const response = await fetch("http://127.0.0.1:8000" + "/api/v1/getMaps");
    let data = await response.json();
    const maps_el = document.querySelector("#maps");

    if (data.length == 0) {
        return null;
    }

    let groups = {};

    for (let i = 0; i < data.length; i++) {
        let name = data[i].group;
        if (name in groups) {
            groups[name].push(data[i]);
        } else {
            groups[name] = [data[i]];
        }
    }

    for (const key in groups) {
        let optGr = createOptionMap(groups[key]);
        if (maps_el) {
            maps_el.appendChild(optGr);
        } else {
            console.error("Элемент #mapSelect не найден в DOM");
        }
    }

    maps_el.addEventListener('change', (event) => generateGraph());
}

createMapsChoose();