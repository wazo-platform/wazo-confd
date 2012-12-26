-- DDL for table record_campaign
DROP TABLE IF EXISTS record_campaign;

CREATE TABLE record_campaign
(
  id serial NOT NULL,
  campaign_name character varying(128) NOT NULL,
  activated boolean NOT NULL,
  base_filename character varying(64) NOT NULL,
  queue_id integer NOT NULL,
  CONSTRAINT record_campaign_pkey PRIMARY KEY (id ),
  CONSTRAINT record_campaign_queue_id_fkey FOREIGN KEY (queue_id)
      REFERENCES queuefeatures (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION
)
WITH (
  OIDS=FALSE
);
ALTER TABLE record_campaign
  OWNER TO asterisk;
  
-- DDL for table recording
CREATE TYPE call_dir_type AS ENUM
  ('incoming',
  'outgoing');
ALTER TYPE call_dir_type
  OWNER TO asterisk;

DROP TABLE IF EXISTS recording;

CREATE TABLE recording
(
  cid character varying(32) NOT NULL,
  call_direction call_dir_type,
  start_time timestamp without time zone,
  end_time timestamp without time zone,
  caller character varying(32),
  client_id character varying(1024),
  callee character varying(32),
  filename character varying(1024),
  agent character varying(40),
  campaign_id integer NOT NULL,
  CONSTRAINT recording_pkey PRIMARY KEY (cid ),
  CONSTRAINT recording_agent_fkey FOREIGN KEY (agent)
      REFERENCES agentfeatures ("number") MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION,
  CONSTRAINT recording_campaign_id_fkey FOREIGN KEY (campaign_id)
      REFERENCES record_campaign (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION
)
WITH (
  OIDS=FALSE
);
ALTER TABLE recording
  OWNER TO asterisk;