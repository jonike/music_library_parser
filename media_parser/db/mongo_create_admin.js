db.createUser(
{
    user: "run_admin_run",
    pwd: "run_pass_run",
    roles: [
      { role: "userAdminAnyDatabase", db: "admin" },
      { role: "readWrite", db: "media_db" }
    ]
});
