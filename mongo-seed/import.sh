#! /bin/bash

mongoimport --host mongodb --db istapp --collection tasks --type json --file mongo-seed/dump/tasks.json --jsonArray
mongoimport --host mongodb --db istapp --collection rooms --type json --file mongo-seed/dump/rooms.json --jsonArray
mongoimport --host mongodb --db istapp --collection roles --type json --file mongo-seed/dump/roles.json --jsonArray
