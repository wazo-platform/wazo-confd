XiVO RestAPI
============

_warning_

   Be sure to pass all tests before submiting any patch.


Acceptance Testing
------------------

WARNING !!! all data will be erased by the acceptance tests use an empty xivo installation.

- The acceptance tests use xivo_dao to test the database. postgres needs to accept connections from the exterior.
  On the XiVO under test, add the following lines to the postgres configuration files:
    - /etc/postgresql/9.1/main/pg_hba.conf : host    all             all             192.168.0.0/16          md5
    - /etc/postgresql/9.1/main/postgres.conf : listen_addresses = '*'

Now you are ready to start the acceptance tests :

    $ PYTHONPATH=.:../../xivo-dao/xivo-dao/ lettuce acceptance/features/                    # starts all tests 
    $ PYTHONPATH=.:../../xivo-dao/xivo-dao/ lettuce acceptance/features/users.feature       # starts user features tests
    $ PYTHONPATH=.:../../xivo-dao/xivo-dao/ lettuce acceptance/features/users.feature -s 3  # starts the third scenario
