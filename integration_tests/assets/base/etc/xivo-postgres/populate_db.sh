#!/bin/bash

# In single user mode, postgres interprets a newline as the end of the SQL command. 
# Therefore, one command MUST always be on the same line

gosu postgres postgres --single asterisk <<EOF

INSERT INTO "entity" (name, displayname, description) VALUES ('xivotest', 'xivotest', '')

INSERT INTO "accesswebservice" (name, login, passwd, obj, description) VALUES ('admin', 'admin', 'proformatique', '', '')

INSERT INTO "context" (name, displayname, contexttype, description, entity) VALUES ('default', 'Default', 'internal', '', 'xivotest')
INSERT INTO "context" (name, displayname, contexttype, description, entity) VALUES ('from-extern', 'Incalls', 'incall', '', 'xivotest')
INSERT INTO "context" (name, displayname, contexttype, description, entity) VALUES ('to-extern', 'Outcalls', 'incall', '', 'xivotest')

INSERT INTO "contextinclude" (context, include) VALUES ('default', 'to-extern')

INSERT INTO "contextnumbers" (context, type, numberbeg, numberend, didlength) VALUES ('default', 'user', '1000', '1999', 0)
INSERT INTO "contextnumbers" (context, type, numberbeg, numberend, didlength) VALUES ('from-extern', 'incall', '1000', '4999', 0)

CREATE DATABASE xivotemplate TEMPLATE asterisk
EOF
