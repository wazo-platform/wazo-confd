INSERT INTO "entity" (name, displayname, description) VALUES ('xivotest', 'xivotest', '');

INSERT INTO "accesswebservice" (name, login, passwd, obj, description) VALUES ('admin', 'admin', 'proformatique', '', '');

INSERT INTO "context" (name, displayname, contexttype, description, entity) 
VALUES 
('default', 'Default', 'internal', '', 'xivotest'),
('from-extern', 'Incalls', 'incall', '', 'xivotest'),
('to-extern', 'Outcalls', 'incall', '', 'xivotest');

INSERT INTO "contextinclude" (context, include) VALUES ('default', 'to-extern');

INSERT INTO "contextnumbers" (context, type, numberbeg, numberend, didlength)
VALUES
('default', 'user', '1000', '1999', 0),
('from-extern', 'incall', '1000', '4999', 0);

CREATE DATABASE xivotemplate TEMPLATE asterisk;
