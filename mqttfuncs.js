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

			d.status =  (d.status === undefined) ? null : d.status;
			d.car = (d.car === undefined) ? "" : d.car;
			d.vel = (d.vel) ? Math.round(d.vel) : "";
			d.alt = (d.alt) ? Math.round(d.alt) + "m" : "";
			var latlon = d.lat + "," + d.lon;
			var tstamp = d.tstamp;
			var weather = d.weather;
			var temp = d.temp;
			var compass = d.compass;

			var loc = (d.geo) ? d.geo : "?";
			var mapslink = '<a href="http://maps.google.com/?q=' + d.lat + ',' + d.lon + '">' + loc + '</a>';

		    var o = {
			topic:		topic,
			status:		d.status,
			vehicle:	d.car,
			kmh:		d.vel,
			alt:		d.alt,
			cog:		compass,
			latlon:		latlon,
			tstamp:		tstamp,
			weather:	weather,
			degrees:	temp,
			location:	mapslink,
		    };
		    upsert(o);

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
			for (n in config.subscribelist) {
				topic = config.subscribelist[n];
				console.log("subscribe to " + topic);
				mqtt.subscribe(topic, {qos: 0});
			}
		},
		onFailure: function (message) {
			console.log(message.errorMessage);
			setTimeout(MQTTconnect, reconnectTimeout);
		}
	};

	/* Connect to MQTT broker */
	mqtt.connect(options);
}
