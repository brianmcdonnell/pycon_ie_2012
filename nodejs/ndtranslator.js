var net = require('net');
var S = require('string');

function translate(host, port, input_str, callback) {
    var output_str = "";
    var client = net.connect({ 'port': port, 'host': host }, function() {
        client.write(input_str);
    });
    client.on('data', function(data) {
        output_str = output_str + data;
        if (S(data).endsWith('.')) {
            client.end();
        }
    });
    client.on('end', function() {
        callback(null, output_str);
    });
    client.on('error', function(e) {
        callback(e);
    });
}

exports.translate = translate;
