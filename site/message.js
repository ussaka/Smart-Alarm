const ws = new WebSocket("ws://localhost:3001");

ws.addEventListener("open", () => {
	requestLayout()
})

ws.addEventListener('message', (event) => {
	const msg = JSON.parse(event.data.toString())
	console.log(msg)

	if(msg.error)
		return;

	if(msg.cmd == "getlayout") {
		setLayout(msg.result[0])
		setValues(msg.result[1])
	}

	else if(msg.cmd == "nodeadd") {
		console.log("node type", msg.type)
		console.log("node name", msg.name)
		console.log("is sensor", msg.sensor)

		addNodeListing(msg.type, msg.name, msg.sensor)
		addNodeFormat(msg.type, msg.format)
	}

	else if(msg.cmd === "depend") {
		if(msg.result === false)
			cutDependency(msg.arg[1], msg.arg[3])
	}

	else if(msg.cmd === "passed") {
		console.log(msg.arg)
		highlightNodeByID(msg.arg[0], msg.arg[1], msg.arg[2] ? "green" : "red")
	}
});

function sendMessage(json)
{
	ws.send(JSON.stringify(json))
}

function requestLayout() {
	sendMessage({
		cmd : "getlayout",
		arg : []
	})

	sendMessage({
		cmd: "instancespassed",
		arg: []
	})
}

function sendLayout(layoutJSON) {
	console.log(layoutJSON)
	sendMessage({
		cmd : "layout",
		arg : [ layoutJSON ]
	})
}

function setParameters(node, params) {
	sendMessage({
		cmd: "parameters",
		arg: [ node.name, node.data.instance, params ]
	})
}

function addDependency(to, node) {
	sendMessage({
		cmd: "depend",
		arg: [ to.name, to.data.instance, node.name, node.data.instance ]
	})
}

function removeDependency(from, node) {
	sendMessage({
		cmd: "undepend",
		arg: [ from.name, from.data.instance, node.name, node.data.instance ]
	})
}

function addInstance(node) {
	console.log("adding instance", node.data.instance)

	sendMessage({
		cmd: "instance",
		arg: [ node.name, node.data.instance ]
	})
}

function removeInstance(id) {
	sendMessage({
		cmd: "removeinstance",
		arg: [ id ]
	})
}
