var http = require("http");
var url = require('url');
var net = require('net');
var S = require('string');

var SVC_PORT = 8010;

var PORT = 8080

http.createServer(function(request, response) {
    if (request.url == '/favicon.ico'){
        response.statusCode = 404;
        response.end();
        return;
    }
    var parts = url.parse(request.url, true);

    var client = net.connect({ port: SVC_PORT }, function() {
        client.write(parts.query.data);
    });
    client.on('data', function(data) {
        response.write(data);
        if (S(data).endsWith('.')) {
            client.end();
        }
    });
    client.on('end', function() {
        response.end();
    });
    client.on('error', function(e) {
        response.writeHeader(500, {"Content-Type": "text/plain"});
        response.write("Internal Server Error: " + e);
        response.end();
        console.log(e);
    });

}).listen(PORT);

console.log("Listening on http://localhost:" + PORT + " params:data");
