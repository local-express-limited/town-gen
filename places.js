const num_to_generate = 60;
const no_end_threshold = 5;

fetch('./places.json')
	.then((response) => response.json())
	.then((data) => {
		const button = document.getElementById("generate");
		button.addEventListener("click", (event) => {
			generate(data);
		});
	});

function generate(place_data) {
	// Clear existing
	const elem = document.getElementById("places");
	for (let child of elem.children) {
		child.innerHTML = "";
	}
	// Generate new
	for (let i = 0; i < num_to_generate; i++) {
		let prefix = generate_prefix(place_data);
		let infix = weighted_random(place_data["infixes"], []);
		let suffix = "";
		if (infix) {
			suffix = generate_name(place_data["names"]);
		}
		let place = prefix + infix + suffix;
		let str = elem.children[i % elem.childElementCount].innerHTML;
		elem.children[i % elem.childElementCount].innerHTML = str + place + "</br>";
	}
}

function generate_prefix(place_data) {
	let prefix_data = place_data["prefixes"];
	let num_names = Number(weighted_random(prefix_data["num_names"], []));
	let excludes = [];
	if (num_names == 0) {
		excludes.push("0");
	}
	let num_heads = Number(weighted_random(prefix_data["num_heads"], excludes));
	let num_tails = Number(weighted_random(prefix_data["num_tails"], excludes));

	let prefix = "";
	for (let i = 0; i < num_heads; i++) {
		let head = weighted_random(prefix_data["heads"], []);
		if (prefix) {
			prefix = prefix + " " + head;
		} else {
			prefix = head;
		}
	}
	for (let i = 0; i < num_names; i++) {
		let name = generate_name(place_data["names"]);
		if (prefix) {
			prefix = prefix + " " + name;
		} else {
			prefix = name;
		}
	}
	for (let i = 0; i < num_tails; i++) {
		let tail = weighted_random(prefix_data["tails"], []);
		if (prefix) {
			prefix = prefix + " " + tail;
		} else {
			prefix = tail;
		}
	}
	return prefix;
}

function generate_name(name_data) {
	// Choose start
	let x = Math.floor(Math.random() * name_data["starts"].length);
	let start = name_data["starts"][x];
	
	// Choose number of ends
	let num_ends = 0;
	if (start.length > no_end_threshold) {
		num_ends = Number(weighted_random(name_data["num_ends"], []));
	} else {
		num_ends = Number(weighted_random(name_data["num_ends"], ["0"]));
	}

	// Choose ends
	let ends = [];
	for (let i = 0; i < num_ends; i++) {
		let pos = i + 1;
		choice = weighted_random(name_data["ends"][pos.toString()], ends);
		ends.push(choice);
	}

	// Output
	let name = start + ends.reverse().join('');
	name = name.replace(/(.)\1\1/g, '$1$1')
	return name;
}

function weighted_random(options, excludes) {
	let results = [];
	let weights = [];
	Object.entries(options).forEach(([key, value]) => {
		if (!excludes.includes(key)) {
			results[results.length] = key;
			if (weights.length == 0) {
				weights[0] = value;
			} else {
				weights[weights.length] = weights[weights.length - 1] + value;
			}
		}
	});
	let x = Math.floor(Math.random() * weights[weights.length - 1]);

	for (let i = 0; i < weights.length; i++) {
		if (weights[i] > x) {
			return results[i];
		}
	}
}
