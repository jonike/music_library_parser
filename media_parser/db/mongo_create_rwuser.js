db.createUser(
{
    user: "rwuser_run",
    pwd: "run_pass_run",
    roles: [
      { role: "readWrite", db: "admin" },
      { role: "readWrite", db: "media_db" }
    ]
});
