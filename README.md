# OwnTracks Livetable

This requires a republisher which can be found in `repub/`. The republisher uses
<del>`vehicles.json` to convert an MQTT topic name to a</del> `tid` for a "car name" which is shown
in the _vehicle_ column. If `tid` isn't available, the last two characters of the
topic are used.

Reverse geocoding is done via Nominatim. In order to lower the load on Nominatim,
we lower the precision of the lat/lon coordinates to three digits (approximately
100m) and perform a lookup, caching that as we go. The "key" into the database
cache is the lat and the lon, e.g. `12.123,8.987`.

Similarly, weather lookups are performed via OpenWeatherMAP, and these lookups
are cached for an hour. This database should be removed periodically.

`config.js` describes the address and port number of the Websocket server, the
topic to which the app should subscribe (correlate this with `tablerepub.py`)
and whether or not to hide the topic column in the app.

## Why a republisher?

It may well be possible to do all this browser-side in JavaScript, but it was
much easier for me to collect the necessary data server-side and provide that
to JS.

