/* JP Mens, August 2014 */
var reconnectTimeout = 3000;
var mqtt;

function MQTTconnect()
{
	mqtt = new Messaging.Client(config.websockethost, config.websocketport,
				"livetable-" + parseInt(Math.random() * 100, 10));

	mqtt.onConnectionLost = function (responseObject) {
		setTimeout(MQTTconnect, reconnectTimeout);
		console.log(responseObject.errorMessage);
	};

	mqtt.onMessageArrived = function (message) {
		topic = message.destinationName;

		try {
			payload = message.payloadString;
			var d = $.parseJSON(payload);
			console.log(topic + " " + payload);

			var stimg;

			var st = d['status'];
			if (st == undefined) {
				stimg = "";
			} else if (st == -1) {
				stimg = '<img src="icons/yellowdot.gif" />';
			} else if (st == 1) {
				stimg = '<img src="icons/greendot.gif" />';
			} else {
				stimg = '<img src="icons/reddot.gif" />';
			}


			var car = (d.car) ? d.car : 'xx';
			var vel = (d.vel) ? Math.round(d.vel) : "";
			var alt = (d.alt) ? Math.round(d.alt) + "m" : "";
			var latlon = d.lat + "," + d.lon;
			var tstamp = d.tstamp;
			var weather = d.weather;
			var temp = d.temp;

			var loc = (d.geo) ? d.geo : "?";
			var mapslink = '<a href="http://maps.google.com/?q=' + d.lat + ',' + d.lon + '">' + loc + '</a>';

			var index = tab.column(0).data().indexOf(topic);
			if (index < 0) {
				var rowNode = tab
					.row.add([topic, stimg, car, vel, alt, latlon, tstamp, weather, temp, mapslink])
					.draw()
					.node();
			} else {
				tab.cell(index, 1).data(stimg).draw();
				tab.cell(index, 2).data(car).draw();
				tab.cell(index, 3).data(vel).draw();
				tab.cell(index, 4).data(alt).draw();
				tab.cell(index, 5).data(latlon).draw();
				tab.cell(index, 6).data(tstamp).draw();
				tab.cell(index, 7).data(weather).draw();
				tab.cell(index, 8).data(temp).draw();
				tab.cell(index, 9).data(mapslink).draw();
			}

		} catch (err) {
			console.log("JSON parse error " + err);
			return;
		}
	};

	var options = {
		timeout: 60,
		useSSL: config.usetls,
		onSuccess: function () {
			console.log("Host: " + config.websockethost + ", Port:" +  config.websocketport);
			mqtt.subscribe(config.subscribe, {qos: 0});
		},
		onFailure: function (message) {
			console.log(message.errorMessage);
			setTimeout(MQTTconnect, reconnectTimeout);
		}
	};

	/* Connect to MQTT broker */
	mqtt.connect(options);
}
