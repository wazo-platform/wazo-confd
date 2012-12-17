-- DDL for table record_campaign
CREATE TABLE record_campaign
(
  campaign_name character varying(128) NOT NULL PRIMARY KEY,
  activated boolean NOT NULL,
  base_filename character varying(64) NOT NULL,
  queue_id integer NOT NULL REFERENCES queuefeatures(id)
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

CREATE TABLE recording
(
  cid character varying(32) NOT NULL PRIMARY KEY,
  campaign_name character varying(128) REFERENCES record_campaign(campaign_name)
      ON UPDATE NO ACTION ON DELETE NO ACTION,
  call_direction call_dir_type,
  start_time timestamp without time zone,
  end_time timestamp without time zone,
  caller character varying(32),
  client_id character varying(1024),
  callee character varying(32),
  agent character varying(40) REFERENCES agentfeatures(number)
      ON UPDATE NO ACTION ON DELETE NO ACTION
)
WITH (
  OIDS=FALSE
);

ALTER TABLE recording
  OWNER TO asterisk;
