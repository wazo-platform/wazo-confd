#!/bin/bash
sed -i 's/#fsync.*/fsync = off/g' /var/lib/postgresql/data/postgresql.conf
