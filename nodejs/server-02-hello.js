var http = require("http");
var url = require('url');

http.createServer(function(request, response) {

    setTimeout(function(){
        var parts = url.parse(request.url, true);
        response.writeHead(200, {"Content-Type": "text/plain"});
        response.write("Hello World " + parts.query.user + " (delayed)");
        response.end();
    }, 1000);

}).listen(8080);

