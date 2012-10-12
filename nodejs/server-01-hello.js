var http = require("http");

var PORT = 8080

http.createServer(function(request, response) {
  response.writeHead(200, {"Content-Type": "text/plain"});
  response.write("Hello World");
  response.end();
}).listen(PORT);

console.log("Listening on http://localhost:" + PORT);
