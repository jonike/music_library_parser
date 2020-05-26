#!/bin/bash
printf "%s starting...\n" "${BASH_SOURCE[0]}"
START=$(date +%s.%N)

printf "removing users from admin/media_db databases\n"
for database in admin media_db
do
    for user in run_admin_run rw_user_run
    do
        mongo $database --eval "db.dropUser('$user')"
    done
done

printf "recreating users to admin/media_db databases\n"
for script in mongo_create_admin mongo_create_rwuser
do
    mongo admin $script.js
done

for database in admin media_db
do
    printf "$database\n"
    mongo $database --eval "db.getUsers()"
done

END=$(date +%s.%N)
RUNTIME=$(echo "$END - $START" | bc)
printf "runtime: %0.3f seconds" "$RUNTIME"

printf "%s complete...\n" "${BASH_SOURCE[0]}"

# mongo admin --eval "db.getUsers()"
# mongo admin --eval "db.dropUser('rw_user_run')"
# mongo admin --eval "db.dropUser('run_admin_run')"
# mongo admin --eval "db.getUsers()"
# mongo media_db mongo_create_admin.js
# mongo media_db drop_mongo_admin.js
# mongo media_db mongo_create_rwuser.js
# mongo media_db --eval "db.dropUser('rw_user_run')"
# mongo media_db --eval "db.dropUser('run_admin_run')"
