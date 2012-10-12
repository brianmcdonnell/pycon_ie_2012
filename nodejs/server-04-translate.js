var http = require("http");
var url = require('url');
var net = require('net');
var translator = require('./ndtranslator');

var SVC_HOST = 'localhost';
var SVC_PORT = 8010;

var PORT = 8080

http.createServer(function(request, response) {
    if (request.url == '/favicon.ico'){
        response.statusCode = 404;
        response.end();
        return;
    }
    var parts = url.parse(request.url, true);

    translator.translate(SVC_HOST, SVC_PORT, parts.query.data, function(err, output_str){
        if (err == null){
            response.write(output_str);
        } else {
            response.statusCode = 500;
            response.write("Internal Server Error: " + err);
        }
        response.end();
    });

}).listen(PORT);

console.log("Listening on http://localhost:" + PORT + " params:data");
