function json_request(method, url, data) {
	data = JSON.stringify(data);
	return new Promise(function (resolve, reject) {
		let xhr = new XMLHttpRequest();
		xhr.open(method, url);
		xhr.onload = function () {
			if (this.status >= 200 && this.status < 300) {
				resolve(this.response);
			} else {
				reject({
					response: this.response,
					status: this.status,
				});
			}
		};
		xhr.onerror = function () {
			reject({
				response: this.response,
				status: this.status,
			});
		};
		xhr.setRequestHeader('Content-Type', 'application/json');
		xhr.send(data);
	});
}

function set_option_visibility(option, visible) {
	let name = option + '_options';
	let option_el = document.getElementById(name);

	if (!option_el) {
		console.warn("Options of '" + name + "' not found");
		return;
	}

	option_el.hidden = !visible;
}

async function call_app(data) {
	result = JSON.parse(await json_request('POST', '/rpc', data));
	if (result['error']) {
		throw new Error(result['error']);
	}

	return result['result'];
}

function create_call(command) {
	data = {
		command: command,
		args: [],
	};

	switch (data['command']) {
		case 'rpc_send':
			data['args'].push(document.getElementById('send_text').value);
			break;

		case 'message':
			data['args'].push(document.getElementById('message_text').value);
			data['args'].push(document.getElementById('as_user').value);
			data['args'].push(document.getElementById('as_channel').value);
			break;

		case 'status':
			break;
		case 'pause':
			break;
		case 'unpause':
			break;
		default:
			throw new Error('Unknown command: ' + data['command'] + "'");
	}

	return data;
}

async function update_loop() {
	update_status();

	// setTimeout(update_loop, 500);
}

async function update_status() {
	let response = await call_app(create_call('status'));

	status_html = '';
	status_html += `Env: ${response['env']}\n`;
	status_html += `Version: ${response['ver']}\n`;
	status_html += `Up since: ${response['up_since']}\n`;
	status_html += `Ready: ${response['ready']}\n`;
	status_html += `Paused: ${response['paused']}\n`;

	document.getElementById('bot_status').innerHTML = status_html;
}

document.addEventListener('DOMContentLoaded', function () {
	document.getElementById('send_btn').addEventListener('click', async function () {
		data = create_call(document.getElementById('command').value);

		let response;
		try {
			response = await call_app(data);
		} catch (e) {
			response = String(e);
		}

		if (typeof response !== 'string') {
			console.info("Received: '" + typeof response + "' converting to JSON");
			response = "JSON: " + JSON.stringify(response, null, 4);
		}

		document.getElementById('bot_response').innerHTML = response;
	});

	let command = document.getElementById('command');
	command.addEventListener('change', async function () {
		let el = document.getElementById('command');

		// Hide all
		for (let option of el.options) {
			set_option_visibility(option.value, false);
		}

		// Show selected
		set_option_visibility(el.value, true);
	});

	// Update HTML
	command.dispatchEvent(new Event('change'));

	update_loop();
});
