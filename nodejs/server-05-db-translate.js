var http = require("http");
var url = require('url');
var net = require('net');
var translator = require('./ndtranslator');
var Db = require('mongodb').Db;
var Server = require('mongodb').Server;

var SVC_HOST = 'localhost';
var SVC_PORT = 8010;
var DB_HOST = 'localhost';
var DB_PORT = 27017;

var PORT = 8080

http.createServer(function(request, response) {
    if (request.url == '/favicon.ico'){
        response.statusCode = 404;
        response.end();
        return;
    }
    var parts = url.parse(request.url, true);
    
    // Connect to mongo
    var server = new Server(DB_HOST, DB_PORT, { auto_reconnect: false });
    var db = new Db('pycon', server, {safe: true});
    db.open(function(err, db) { 
        db.collection('users', function(err, users_col) {
            users_col.findOne({name: parts.query.user}, function(err, user) {
                if (user == null){
                    response.statusCode = 403;
                    response.write("Insufficient Funds");
                    response.end();
                } else {
                    // We have a valid user, so do the translation
                    doTranslate();
                }
                db.close();
            });
        });
    });

    function doTranslate() {
        translator.translate(SVC_HOST, SVC_PORT, parts.query.data, function(err, output_str){
            if (err == null) {
                response.write(output_str);
            } else {
                response.statusCode = 500;
                response.write("Internal Server Error: " + err);
            }
            response.end();
        });
    }

}).listen(PORT);

console.log("Listening on http://localhost:" + PORT + " params:data,user");
