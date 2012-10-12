var http = require("http");
var url = require('url');
var translator = require('./ndtranslator');
var Db = require('mongodb').Db;
var Server = require('mongodb').Server;
var async = require('async');

var SVC_HOST = 'localhost';
var SVC_PORT = 8010;
var DB_HOST = 'localhost';
var DB_PORT = 27017;

var PORT = 8080;

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

    // Use async waterfall pattern to avoid deep nesting.
    async.waterfall([
        function(callback) {
            db.open(callback);
        },
        function(db, callback) {
            db.collection('users', callback);
        },
        function(users_col, callback) {
            users_col.findOne({name: parts.query.user}, callback);
        },
        function(user, callback) {
            if (user == null){
                response.statusCode = 403;
                response.write("User not found.");
                response.end();
            } else {
                console.log("Found user " + user.name);
                doTranslate();
            }
            db.close();
        },
    ],
    function (err, result) {
        response.statusCode = 500;
        response.write("Internal Server Error: " + err);
    });

    function doTranslate() {
        console.log("Translating " + parts.query.data);
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

console.log("Listening on http://localhost:" + PORT);
