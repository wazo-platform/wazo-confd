--script SQL à exécuter avant les tests unitaires
INSERT INTO queuefeatures(id, name, displayname) VALUES (1, 'name', 'displayname');
INSERT INTO queuefeatures(id, name, displayname) VALUES (2, 'name', 'displayname');
INSERT INTO agentfeatures(id, numgroup, number, passwd, context, language, description) VALUES 
(1, 1, '1000', '1000', 'default', 'fr_FR', 'my_agent');
