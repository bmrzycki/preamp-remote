function fetch(a) {
    let h = new XMLHttpRequest();
    h.onerror = function(error) {
	tabClear();
	document.getElementById("tab.error").style.display = "block";
    };
    h.onreadystatechange = function() {
	if (this.readyState == 4 && this.status == 200) {
	    let data = JSON.parse(h.responseText);
	    handler(data);
	}
    };
    h.open("POST", "/1", true);
    h.send(JSON.stringify(a));
}

function statNum(value) {
    let tmp = value;
    if (value.indexOf('(') != -1 && value.indexOf(')') != -1) {
	tmp = value.split('(')[1].split(')')[0];
    }
    tmp = parseInt(tmp);
    if (Number.isNaN(tmp)) {
	return -1;
    }
    return `${tmp}`;
}

function handler(data) {
    let d = {}, pad = 0;
    for (let i in data) {
	let cmd = data[i];
	if (debugMode) {
	    console.log(`handler: req_raw=${cmd['req_raw']}`);
	}
	for (let j in cmd['responses']) {
	    let rsp = cmd['responses'][j];
	    if (debugMode) {
		console.log(`  ${rsp}`);
	    }

	    if (rsp.startsWith("ERR ")) {
		console.log(`handler: ${rsp} ${cmd}`);
	    }

	    let sp = rsp.split(' ');
	    if (sp[0].toLowerCase() != 'sy') {
		continue;
	    }

	    let name = sp[1].toLowerCase(), sx = "";
	    let value = sp.slice(2).join(' ');
	    pad = Math.max(pad, name.length);

	    if (name === "ac") {
		sx = " volts"
	    } else if (name === "temp") {
		sx = " c"
	    } else if (name === "mode") {
		let num = statNum(value);
		if (num != -1) {
		    document.getElementById("pd.mode").value = num;
		}
	    }
	    d[name] = `${value}${sx}`;
	}
    }

    if (document.getElementById("tab.info").style.display !== "block") {
	return;
    }

    let str = "", a = [];
    for (let i in d) {
	a.push(i);
    }
    a = a.sort();
    for (let i in a) {
	let key = a[i];
	str += " ".repeat(1 + (pad - key.length));
        str += `${key}: ${d[key]}\n`;
    }
    document.getElementById("ta.info").value = str;
}

function tabClear() {
    // Hide all tab panel views.
    let x = document.getElementsByClassName("tab_view");
    for (let i = 0; i < x.length; i++) {
	x[i].style.display = "none";
    }
    // Deselect all tab buttons.
    x = document.getElementsByClassName("btn_tab");
    for (let i = 0; i < x.length; i++) {
	x[i].style.color = colorBar;
	x[i].style.backgroundColor = "transparent";
    }
}

function tabOpenJS(name) {
    tabClear();
    // Highlight selected tab button.
    let e = document.getElementById(`btn_tab.${name}`);
    e.style.color = "black";
    e.style.backgroundColor = colorBar;

    // Display selected tab panel view.
    document.getElementById(`tab.${name}`).style.display = "block";

    // Update selected tab panel view information.
    if (name === "main") {
	fetch(["stat off", "stat mode"]);
    } else if (name === "trim") {
	fetch(["stat off"]);
    } else if (name === "remote") {
	fetch(["stat off"]);
    } else if (name === "info") {
	document.getElementById("ta.info").value = "  loading...";
	fetch(["stat off", "stat mode", "stat audio", "stat video",
	       "stat temp", "stat vers", "stat ac", "stat swvers",
	       "stat hostinfo", "stat main"]);
    }
}

function tabOpen() {
    tabOpenJS(event.target.id.split(".")[1]);
}

function cmd() {
    let sp = event.target.id.split(".");
    let kind = sp[0];
    let name = sp[1];
    let cmd = name; // default: kind === "cmd"

    if (debugMode) {
	console.log(`cmd: sp=${sp}`);
    }

    if (kind === "irc") {
	cmd = `${kind} ${name}`;
    } else if (kind === "pd") {
	let val = event.target.value;
	cmd = mapIR[name][val] ? `irc ${mapIR[name][val]}` : "";
    } else if (mapIR[kind]) {
	cmd = mapIR[kind][name] ? `irc ${mapIR[kind][name]}` : "";
    }

    if (cmd) {
	let cmds = [cmd];
	if (debugMode) {
	    console.log(`cmd: id=${event.target.id} cmds=${cmds}`);
	}
	fetch(cmds);
    }
}

var debugMode = false;
const urlParams = new URLSearchParams(location.search);
if (urlParams.has("debug")) {
    debugMode = true;
    console.log("debug mode enabled");
}

const colorBar  = "#C0C0C0";
const mapIR = {
    "mode" : {
	"0"  : "193",
	"1"  : "194",
	"2"  : "195",
	"3"  : "196",
	"4"  : "197",
	"5"  : "198",
	"6"  : "199",
	"7"  : "200",
	"8"  : "201",
	"9"  : "202",
	"10" : "211",
	"11" : "203",
	"12" : "204",
	"13" : "205",
	"14" : "206",
	"15" : "207",
	"16" : "208",
	"17" : "209",
    },
    "input" : {
	"1"  : "2",
	"2"  : "3",
	"3"  : "4",
	"4"  : "5",
	"5"  : "6",
	"6"  : "7",
	"7"  : "8",
	"8"  : "9",
	"9"  : "120",
	"10" : "121",
	"11" : "122",
	"12" : "123",
	"13" : "124",
	"14" : "125",
	"15" : "126",
	"16" : "127",
	"17" : "128",
	"18" : "129",
	"19" : "130",
	"20" : "131",
    },
    "config" : {
	"1" : "185",
	"2" : "186",
	"3" : "187",
	"4" : "188",
	"5" : "189",
	"6" : "190",
    },
};
tabOpenJS("main");  // First tab opened.
