--script SQL à exécuter avant les tests unitaires
DELETE FROM recording;
DELETE FROM record_campaign;
DELETE FROM agentfeatures WHERE id = 1;
DELETE FROM queuefeatures WHERE id = 1 OR id = 2;

INSERT INTO queuefeatures(id, name, displayname) VALUES (1, 'name1', 'displayname');
INSERT INTO queuefeatures(id, name, displayname) VALUES (2, 'name2', 'displayname');
INSERT INTO agentfeatures(id, numgroup, number, passwd, context, language, description) VALUES 
(1, 1, '1000', '1000', 'default', 'fr_FR', 'my_agent');
