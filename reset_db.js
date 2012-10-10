db.users.remove({ name : "brian"});
db.users.save({ name : "brian", balance: 1000, password: "secret" });
