var http = require("http");
var url = require('url');

var PORT = 8080

http.createServer(function(request, response) {

    setTimeout(function(){
        var parts = url.parse(request.url, true);
        response.writeHead(200, {"Content-Type": "text/plain"});
        response.write("Hello World " + parts.query.user + " (delayed)");
        response.end();
    }, 1000);

}).listen(PORT);

console.log("Listening on http://localhost:" + PORT);
