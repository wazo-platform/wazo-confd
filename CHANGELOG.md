Changelog
=========

18.08
-----

* New readonly parameters have been added to the outcall resource:

  * `tenant_uuid`

* New readonly parameters have been added to the incall resource:

  * `tenant_uuid`

* New readonly parameters have been added to the group resource:

  * `tenant_uuid`

* A new API for associating user with a queue has been added:

  * PUT `/1.1/queues/<queue_id>/members/users/<user_id>`
  * DELETE `/1.1/queues/<queue_id>/members/users/<user_id>`

* The following URLs have been deprecated. Please use the new API instead:

  * POST `/1.1/queues/<queue_id>/members/agents`
  * GET `/1.1/queues/<queue_id>/members/agents/<agent_id>`

* New readonly parameters have been added to the queue resource:

  * `members`

    * `agents`
    * `users`

* New readonly parameters have been added to the agent resource:

  * `queues`

* New readonly parameters have been added to the user resource:

  * `queues`
  * `tenant_uuid`

* New parameter have been added to the queue-member agent association:

  * `priority`

* The following endpoint does not return an error (400) when the resources are not already associated.
  Instead, it associate resources and return a successful association code (204).

  * PUT `/1.1/queues/<queue_id>/members/agents/<agent_id>`

* The following endpoint does not return a (400) error when the resources are not associated.
  Instead, it returns a successful dissociation code (204).

  * DELETE `/1.1/queues/<queue_id>/members/agents/<agent_id>`

* A new API for associating a queue with a schedule has been added:

  * DELETE `/1.1/queues/<queue_id>/schedules/<schedule_id>`
  * PUT `/1.1/queues/<queue_id>/schedules/<schedule_id>`

* The `/incalls` routes are now multi-tenant. This means that created incalls will be in the same
  tenant as the creator or in the tenant specified by the Wazo-Tenant HTTP header. Listing incalls
  will also only list incalls in the user's tenant unless a sub-tenant is specified using the
  Wazo-Tenant header. The `recurse=true` query string can be used to list from multiple tenants.
  GET, DELETE and PUT on a context that is not in a tenant accessible to the user will result in a
  404.


18.07
-----

* The `/extensions` routes are now multi-tenant. This means that created tenant will be in the same
  tenant as the creator or in the tenant specified by the Wazo-Tenant HTTP header. Listing
  extensions will also only list extensions in the user's tenant unless a sub-tenant is specified using
  the Wazo-Tenant header. The `recurse=true` query string can be used to list from multiple tenants.
  GET, DELETE and PUT on a extension that is not in a tenant accessible to the user will result in a
  404.


* A new API for associating an extension with a queue has been added:

  * DELETE `/1.1/queues/<queue_id>/extensions/<extension_id>`
  * PUT `/1.1/queues/<queue_id>/extensions/<extension_id>`

* A new API for editing fallbacks for a queue has been added:

  * GET `/1.1/queues/<queue_id>/fallbacks`
  * PUT `/1.1/queues/<queue_id>/fallbacks`

* A new API for including contexts inside context has been added:

  * PUT `/1.1/contexts/<context_id>/contexts`

* Added agent endpoints:

  * GET `/1.1/agents`
  * POST `/1.1/agents`
  * DELETE `/1.1/agents/<agent_id>`
  * GET `/1.1/agents/<agent_id>`
  * PUT `/1.1/agents/<agent_id>`

* The entity of a user cannot be changed anymore. The following resource has been removed:

  * PUT `/1.1/users/<user_id>/entities/<entity_id>`

* Added queue endpoints:

  * GET `/1.1/queues`
  * POST `/1.1/queues`
  * DELETE `/1.1/queues/<queue_id>`
  * GET `/1.1/queues/<queue_id>`
  * PUT `/1.1/queues/<queue_id>`


18.06
-----

* A new API for associating users and groups with a call pickup has been added:

  * PUT `/1.1/callpickups/<call_pickup_id>/interceptors/groups`
  * PUT `/1.1/callpickups/<call_pickup_id>/interceptors/users`
  * PUT `/1.1/callpickups/<call_pickup_id>/targets/groups`
  * PUT `/1.1/callpickups/<call_pickup_id>/targets/users`


* The `/contexts` routes are now multi-tenant. This means that created tenant will be in the same
  tenant as the creator or in the tenant specified by the Wazo-Tenant HTTP header. Listing contexts
  will also only list contexts in the user's tenant unless a sub-tenant is specified using the
  Wazo-Tenant header. The `recurse=true` query string can be used to list from multiple tenants.
  GET, DELETE and PUT on a context that is not in a tenant accessible to the user will result in a
  404.


18.05
-----

* Added call pickup endpoints:

  * GET `/1.1/callpickups`
  * POST `/1.1/callpickups`
  * DELETE `/1.1/callpickups/<call_pickup_id>`
  * GET `/1.1/callpickups/<call_pickup_id>`
  * PUT `/1.1/callpickups/<call_pickup_id>`


18.04
-----

* The `password` field has been removed from GET `/1.1/users/export`
* The `Wazo-Tenant` header can now be used when creating users in a given tenant.

    * POST `/1.1/users`
    * POST `/1.1/users/import`

* The users GET, PUT and DELETE are now filtered by tenant. xivo-confd will behave as if users from other tenants do not exist.


18.02
-----

* A new API for editing fallbacks for a call filter has been added:

  * GET `/1.1/callfilters/<call_filter_id>/fallbacks`
  * PUT `/1.1/callfilters/<call_filter_id>/fallbacks`

* A new API for associating users with a call filter has been added:

  * PUT `/1.1/callfilters/<call_filter_id>/recipients/users`
  * PUT `/1.1/callfilters/<call_filter_id>/surrogates/users`

* Added call filter endpoints:

  * GET `/1.1/callfilters`
  * POST `/1.1/callfilters`
  * DELETE `/1.1/callfilters/<call_filter_id>`
  * GET `/1.1/callfilters/<call_filter_id>`
  * PUT `/1.1/callfilters/<call_filter_id>`

* A new API for updating all template's funckeys

  * PUT `/1.1/funckeys/templates/<template_id>`


18.01
-----

* Added register iax endpoints:

  * GET `/1.1/registers/iax`
  * POST `/1.1/registers/iax`
  * DELETE `/1.1/registers/iax/<register_iax_id>`
  * GET `/1.1/registers/iax/<register_iax_id>`
  * PUT `/1.1/registers/iax/<register_iax_id>`

* The following endpoints do not return an error (400) when the resources are already associated. Instead, they return a successful association code (204).

  * PUT `/1.1/conferences/<id>/extensions/<id>`
  * PUT `/1.1/groups/<id>/extensions/<id>`
  * PUT `/1.1/groups/<id>/schedules/<id>`
  * PUT `/1.1/incalls/<id>/extensions/<id>`
  * PUT `/1.1/incalls/<id>/schedules/<id>`
  * PUT `/1.1/lines/<id>/devices/<id>`
  * PUT `/1.1/lines/<id>/endpoints/sip/<id>`
  * PUT `/1.1/lines/<id>/endpoints/sccp/<id>`
  * PUT `/1.1/lines/<id>/endpoints/custom/<id>`
  * PUT `/1.1/lines/<id>/extensions/<id>`
  * PUT `/1.1/outcalls/<id>/callpermissions/<id>`
  * PUT `/1.1/outcalls/<id>/extensions/<id>`
  * PUT `/1.1/outcalls/<id>/schedules/<id>`
  * PUT `/1.1/parkinglots/<id>/extensions/<id>`
  * PUT `/1.1/trunks/<id>/endpoints/sip/<id>`
  * PUT `/1.1/trunks/<id>/endpoints/custom/<id>`
  * PUT `/1.1/users/<id>/agents/<id>`
  * PUT `/1.1/users/<id>/callpermissions/<id>`
  * PUT `/1.1/users/<id>/entities/<id>`
  * PUT `/1.1/users/<id>/lines/<id>`
  * PUT `/1.1/users/<id>/schedules/<id>`
  * PUT `/1.1/users/<id>/voicemails/<id>`

* The following endpoints do not return an error (400) when the resources are already dissociated. Instead, they return a successful dissociation code (204).

  * DELETE `/1.1/conferences/<id>/extensions/<id>`
  * DELETE `/1.1/groups/<id>/extensions/<id>`
  * DELETE `/1.1/groups/<id>/schedules/<id>`
  * DELETE `/1.1/incalls/<id>/extensions/<id>`
  * DELETE `/1.1/incalls/<id>/schedules/<id>`
  * DELETE `/1.1/lines/<id>/devices/<id>`
  * DELETE `/1.1/lines/<id>/endpoints/sip/<id>`
  * DELETE `/1.1/lines/<id>/endpoints/sccp/<id>`
  * DELETE `/1.1/lines/<id>/endpoints/custom/<id>`
  * DELETE `/1.1/lines/<id>/extensions/<id>`
  * DELETE `/1.1/outcalls/<id>/callpermissions/<id>`
  * DELETE `/1.1/outcalls/<id>/extensions/<id>`
  * DELETE `/1.1/outcalls/<id>/schedules/<id>`
  * DELETE `/1.1/parkinglots/<id>/extensions/<id>`
  * DELETE `/1.1/trunks/<id>/endpoints/sip/<id>`
  * DELETE `/1.1/trunks/<id>/endpoints/custom/<id>`
  * DELETE `/1.1/users/<id>/agents`
  * DELETE `/1.1/users/<id>/callpermissions/<id>`
  * DELETE `/1.1/users/<id>/lines/<id>`
  * DELETE `/1.1/users/<id>/funckeys/templates/<id>`
  * DELETE `/1.1/users/<id>/schedules/<id>`
  * DELETE `/1.1/users/<id>/voicemails`

* Added SCCP general endpoints:

  * GET `/1.1/asterisk/sccp/general`
  * PUT `/1.1/asterisk/sccp/general`

* Added IAX CallNumberLimits endpoints:

  * GET `/1.1/asterisk/iax/callnumberlimits`
  * PUT `/1.1/asterisk/iax/callnumberlimits`

* Added ConfBridge default_bridge endpoints:

  * GET `/1.1/asterisk/confbridge/default_bridge`
  * PUT `/1.1/asterisk/confbridge/default_bridge`

* Added ConfBridge default_user endpoints:

  * GET `/1.1/asterisk/confbridge/default_user`
  * PUT `/1.1/asterisk/confbridge/default_user`

* Added Features applicationmap endpoints:

  * GET `/1.1/asterisk/features/applicationmap`
  * PUT `/1.1/asterisk/features/applicationmap`

* Added Features featuremap endpoints:

  * GET `/1.1/asterisk/features/featuremap`
  * PUT `/1.1/asterisk/features/featuremap`

* Added Features general endpoints:

  * GET `/1.1/asterisk/features/general`
  * PUT `/1.1/asterisk/features/general`

* A new API for managing :abbr:`Sounds`:

  * GET `/1.1/sounds`
  * POST `/1.1/sounds`
  * DELETE `/1.1/sounds/<sound_id>`
  * GET `/1.1/sounds/<sound_id>`
  * PUT `/1.1/sounds/<sound_id>`
  * DELETE `/1.1/sounds/<sound_id>/files/<filename>`
  * GET `/1.1/sounds/<sound_id>/files/<filename>`
  * PUT `/1.1/sounds/<sound_id>/files/<filename>`

* Added extension feature endpoints:

  * GET `/1.1/extensions/features`
  * GET `/1.1/extensions/features/<extension_id>`
  * PUT `/1.1/extensions/features/<extension_id>`

* New parameters have been added to the extension resource:

  * `enabled`

* Parameters have been deprecated for the extension resource:

  * `commented`

* Added iax endpoints:

  * GET `/1.1/endpoints/iax`
  * POST `/1.1/registers/iax`
  * DELETE `/1.1/endpoints/iax/<endpoint_iax_id>`
  * GET `/1.1/endpoints/iax/<endpoint_iax_id>`
  * PUT `/1.1/endpoints/iax/<endpoint_iax_id>`

* A new API for associating an endpoint iax with a trunk has been added:

  * DELETE `/1.1/trunks/<trunk_id>/endpoints/iax/<endpoint_id>`
  * PUT `/1.1/trunks/<trunk_id>/endpoints/iax/<endpoint_id>`

* New parameters have been added to the endpoint custom resource:

  * `interface_suffix`

* A new API for associating registers with a trunk has been added:

  * DELETE `/1.1/trunks/<trunk_id>/registers/iax/<register_id>`
  * PUT `/1.1/trunks/<trunk_id>/registers/iax/<register_id>`
  * DELETE `/1.1/trunks/<trunk_id>/registers/sip/<register_id>`
  * PUT `/1.1/trunks/<trunk_id>/registers/sip/<register_id>`


17.17
-----

* Added register sip endpoints:

  * GET `/1.1/registers/sip`
  * POST `/1.1/registers/sip`
  * DELETE `/1.1/registers/sip/<register_sip_id>`
  * GET `/1.1/registers/sip/<register_sip_id>`
  * PUT `/1.1/registers/sip/<register_sip_id>`

* Added Timezones endpoints:

  * GET `/1.1/timezones`

* Added Sounds Languages endpoints:

  * GET `/1.1/sounds/languages`

* A new API for associating a outcall with a call permission has been added:

  * PUT `/1.1/outcalls/<outcall_id>/callpermissions/<call_permission_id>`
  * DELETE `/1.1/outcalls/<outcall_id>/callpermissions/<call_permission_id>`

* A new API for associating group with a call permission has been added:

  * PUT `/1.1/groups/<group_id>/callpermissions/<call_permission_id>`
  * DELETE `/1.1/groups/<group_id>/callpermissions/<call_permission_id>`

* Added IAX general endpoints:

  * GET `/1.1/asterisk/iax/general`
  * PUT `/1.1/asterisk/iax/general`

* Added Voicemail general endpoints:

  * GET `/1.1/asterisk/voicemail/general`
  * PUT `/1.1/asterisk/voicemail/general`


17.16
-----

* Added Voicemail ZoneMessages endpoints:

  * GET `/1.1/asterisk/voicemail/zonemessages`
  * PUT `/1.1/asterisk/voicemail/zonemessages`

* A new API to know if user exists has been added:

  * HEAD `/1.1/users/<user_uuid>`

* A new API for associating extensions with a group has been added:

  * PUT `/1.1/groups/<group_id>/members/extensions`

* A new API for associating an user with a schedule has been added:

  * DELETE `/1.1/users/<user_id>/schedules/<schedule_id>`
  * PUT `/1.1/users/<user_id>/schedules/<schedule_id>`

* A new API for associating an group with a schedule has been added:

  * DELETE `/1.1/groups/<group_id>/schedules/<schedule_id>`
  * PUT `/1.1/groups/<group_id>/schedules/<schedule_id>`

* A new API for associating an outcall with a schedule has been added:

  * DELETE `/1.1/outcalls/<outcall_id>/schedules/<schedule_id>`
  * PUT `/1.1/outcalls/<outcall_id>/schedules/<schedule_id>`


17.13
-----

* A line that is associated to a device can now be deleted
* A new API for user's services has been added:

  * PUT `/1.1/users/<user_id>/services`


17.10
-----

* A new API for associating lines with a user has been added:

  * PUT `/1.1/users/<user_uuid>/lines`


17.09
-----

* A new API for associating groups with a user has been added:

  * PUT `/1.1/users/<user_uuid>/groups`


17.05
-----

* New readonly parameters have been added to the user resource:

  * `agent`


17.03
-----

* A new API for managing :abbr:`MOH (Music On Hold)`:

  * GET `/1.1/moh`
  * POST `/1.1/moh`
  * DELETE `/1.1/moh/<moh_id>`
  * GET `/1.1/moh/<moh_id>`
  * PUT `/1.1/moh/<moh_id>`
  * DELETE `/1.1/moh/<moh_id>/files/<filename>`
  * GET `/1.1/moh/<moh_id>/files/<filename>`
  * PUT `/1.1/moh/<moh_id>/files/<filename>`


17.02
-----

* Added schedules endpoints:

  * GET `/1.1/schedules`
  * POST `/1.1/schedules`
  * DELETE `/1.1/schedules/<schedule_id>`
  * GET `/1.1/schedules/<schedule_id>`
  * PUT `/1.1/schedules/<schedule_id>`

* A new API for associating an incall with a schedule has been added:

  * DELETE `/1.1/incalls/<incall_id>/schedules/<schedule_id>`
  * PUT `/1.1/incalls/<incall_id>/schedules/<schedule_id>`

* A new API for managing switchboards:

  * GET `/1.1/switchboards`
  * POST `/1.1/switchboards`
  * DELETE `/1.1/switchboards/<switchboard_uuid>`
  * GET `/1.1/switchboards/<switchboard_uuid>`
  * PUT `/1.1/switchboards/<switchboard_uuid>`
  * PUT `/1.1/switchboards/<switchboard_uuid>/members/users`


17.01
-----

* Added `conference` destination type for incalls and ivr.

* Added parkinglots endpoints:

  * GET `/1.1/parkinglots`
  * POST `/1.1/parkinglots`
  * DELETE `/1.1/parkinglots/<parking_lot_id>`
  * GET `/1.1/parkinglots/<parking_lot_id>`
  * PUT `/1.1/parkinglots/<parking_lot_id>`

* A new API for associating an extension with a parking_lot has been added:

  * DELETE `/1.1/parkinglots/<parking_lot_id>/extensions/<extension_id>`
  * PUT `/1.1/parkinglots/<parking_lot_id>/extensions/<extension_id>`

* New readonly parameters have been added to the funckeys resource:

  * For destinations of type `user`:

      * `user_firstname`
      * `user_lastname`

  * For destinations of type `group`:

      * `group_name`

* New readonly parameters have been added to the infos resource:

  * `wazo_version`

* Added pagings endpoints:

  * GET `/1.1/pagings`
  * POST `/1.1/pagings`
  * DELETE `/1.1/pagings/<paging_id>`
  * GET `/1.1/pagings/<paging_id>`
  * PUT `/1.1/pagings/<paging_id>`

* A new API for associating users with a paging has been added:

  * PUT `/1.1/pagings/<paging_id>/members/users`
  * PUT `/1.1/pagings/<paging_id>/callers/users`


16.16
-----

* The `conference` destination type in incalls endpoints has been renamed to `meetme`

* Added conferences endpoints:

  * GET `/1.1/conferences`
  * POST `/1.1/conferences`
  * DELETE `/1.1/conferences/<conference_id>`
  * GET `/1.1/conferences/<conference_id>`
  * PUT `/1.1/conferences/<conference_id>`

* A new API for associating an extension with a conference has been added:

  * DELETE `/1.1/conferences/<conference_id>/extensions/<extension_id>`
  * PUT `/1.1/conferences/<conference_id>/extensions/<extension_id>`

* Added groups endpoints:

  * GET `/1.1/groups`
  * POST `/1.1/groups`
  * DELETE `/1.1/groups/<group_id>`
  * GET `/1.1/groups/<group_id>`
  * PUT `/1.1/groups/<group_id>`

* A new API for associating an extension with a group has been added:

  * DELETE `/1.1/groups/<group_id>/extensions/<extension_id>`
  * PUT `/1.1/groups/<group_id>/extensions/<extension_id>`

* A new API for editing fallbacks for a group has been added:

  * GET `/1.1/groups/<group_id>/fallbacks`
  * PUT `/1.1/groups/<group_id>/fallbacks`

* A new API for associating users with a group has been added:

  * PUT `/1.1/groups/<group_id>/members/users`

* Added contexts endpoints:

  * GET `/1.1/contexts`
  * POST `/1.1/contexts`
  * DELETE `/1.1/contexts/<context_id>`
  * GET `/1.1/contexts/<context_id>`
  * PUT `/1.1/contexts/<context_id>`

* A new API for editing fallbacks for a user has been added:

  * GET `/1.1/users/<user_id>/fallbacks`
  * PUT `/1.1/users/<user_id>/fallbacks`

* New readonly parameters have been added to the incall resource:

  * For destinations of type `ivr`:

      * `ivr_name`

  * For destinations of type `user`:

      * `user_firstname`
      * `user_lastname`

  * For destinations of type `voicemail`:

      * `voicemail_name`

* New readonly parameters have been added to the voicemail resource:

  * `users`

* New readonly parameters have been added to the user resource:

  * `voicemail`
  * `incalls`


16.14
-----

* Added users endpoints in REST API:

  * GET `/1.1/users/<user_uuid>/lines/<line_id>/associated/endpoints/sip`

* New readonly parameters have been added to the line resource:

  * `endpoint_sip`
  * `endpoint_sccp`
  * `endpoint_custom`
  * `extensions`
  * `users`

* New readonly parameters have been added to the extension resource:

  * `lines`

* New readonly parameters have been added to the user resource:

  * `lines`

* A new readonly parameter have been added to the endpoint_sip, endpoint_sccp and endpoint_custom
  resource:

  * `line`

* Added outcalls endpoints:

  * GET `/1.1/outcalls`
  * POST `/1.1/outcalls`
  * DELETE `/1.1/outcalls/<outcall_id>`
  * GET `/1.1/outcalls/<outcall_id>`
  * PUT `/1.1/outcalls/<outcall_id>`

* Added IVR endpoints:

  * GET `/1.1/ivr`
  * POST `/1.1/ivr`
  * DELETE `/1.1/ivr/<ivr_id>`
  * GET `/1.1/ivr/<ivr_id>`
  * PUT `/1.1/ivr/<ivr_id>`

* A new API for associating trunks with an outcall has been added:

  * PUT `/1.1/outcalls/<outcall_id>/trunks`

* A new API for associating an extension with an outcall has been added:

  * DELETE `/1.1/outcalls/<outcall_id>/extensions/<extension_id>`
  * PUT `/1.1/outcalls/<outcall_id>/extensions/<extension_id>`


16.13
-----

* New readonly parameters have been added to the trunks resource:

  * `endpoint_sip`
  * `endpoint_custom`

* A new readonly parameter have been added to the endpoint_sip and endpoint_custom resource:

  * `trunk`

* A new API for associating an extension with an incall has been added:

  * DELETE `/1.1/incalls/<incall_id>/extensions/<extension_id>`
  * PUT `/1.1/incalls/<incall_id>/extensions/<extension_id>`

* Added incalls endpoints:

  * GET `/1.1/incalls`
  * POST `/1.1/incalls`
  * DELETE `/1.1/incalls/<incall_id>`
  * GET `/1.1/incalls/<incall_id>`
  * PUT `/1.1/incalls/<incall_id>`


16.12
-----

* A new API for associating an endpoint with a trunk has been added:

  * DELETE `/1.1/trunks/<trunk_id>/endpoints/sip/<endpoint_id>`
  * PUT `/1.1/trunks/<trunk_id>/endpoints/sip/<endpoint_id>`
  * GET `/1.1/trunks/<trunk_id>/endpoints/sip`
  * GET `/1.1/endpoints/sip/<endpoint_id>/trunks`

  * DELETE `/1.1/trunks/<trunk_id>/endpoints/custom/<endpoint_id>`
  * PUT `/1.1/trunks/<trunk_id>/endpoints/custom/<endpoint_id>`
  * GET `/1.1/trunks/<trunk_id>/endpoints/custom`
  * GET `/1.1/endpoints/custom/<endpoint_id>/trunks`

* Added trunks endpoints:

  * GET `/1.1/trunks`
  * POST `/1.1/trunks`
  * DELETE `/1.1/trunks/<trunk_id>`
  * GET `/1.1/trunks/<trunk_id>`
  * PUT `/1.1/trunks/<trunk_id>`

* Added SIP general endpoints:

  * GET `/1.1/asterisk/sip/general`
  * PUT `/1.1/asterisk/sip/general`


16.11
-----

* A new API for associating a user with an agent has been added:

  * DELETE `/1.1/users/<user_id>/agents`
  * GET `/1.1/users/<user_id>/agents`
  * PUT `/1.1/users/<user_id>/agents/<agent_id>`

* A new API to list lines associated to an extension

  * GET `/1.1/extensions/<extension_id>/lines`


* The following URLs have been deprecated. Please use the new API instead:

  * GET `/1.1/extensions/<extension_id>/line`


16.10
-----

* Add possibility to associate many lines to the same user.
* Add possibility to associate many extensions to the same line (only if these lines are
  associated to the same user).
* A new API for associating a user with a voicemail has been added:

  * DELETE `/1.1/users/<user_id>/voicemails`
  * GET `/1.1/users/<user_id>/voicemails`
  * PUT `/1.1/users/<user_id>/voicemails`

* A new API for associating a line with an extension has been added:

  * PUT `/1.1/lines/<line_id>/extensions/<extension_id>`

* A new API for associating a user with a line has been added:

  * PUT `/1.1/users/<user_id>/lines/<line_id>`

* The following URLs have been deprecated. Please use the new API instead:

  * DELETE `/1.1/users/<user_id>/voicemail`
  * GET `/1.1/users/<user_id>/voicemail`
  * POST `/1.1/users/<user_id>/voicemail`
  * POST `/1.1/users/<user_id>/lines`
  * POST `/1.1/lines/<line_id>/extensions`


16.09
-----

* Added entities endpoints:

  * GET `/1.1/entities`
  * POST `/1.1/entities`
  * GET `/1.1/entities/<entity_id>`
  * DELETE `/1.1/entities/<entity_id>`

* A new API for updating all user's funckeys

  * PUT `/1.1/users/<user_id>/funckeys`

* A new parameter have been added to the users resource:

  * `dtmf_hangup_enabled`


16.06
-----

* A new API for initializing a Wazo (passing the wizard):

  * GET `/1.1/wizard`
  * POST `/1.1/wizard`
  * GET `/1.1/wizard/discover`

* A new API for associating a user with an entity has been added:

  * GET `/1.1/users/<user_id>/entities`
  * PUT `/1.1/users/<user_id>/entities/<entity_id>`


16.05
-----

* A new API for associating a user with a call permission has been added:

  * GET `/1.1/users/<user_id>/callpermissions`
  * PUT `/1.1/users/<user_id>/callpermissions/<call_permission_id>`
  * DELETE `/1.1/users/<user_id>/callpermissions/<call_permission_id>`
  * GET `/1.1/callpermissions/<call_permission_id>/users`

* Two new parameters have been added to the users resource:

  * `call_permission_password`
  * `enabled`

* A new API for user's forwards has been added:

  * PUT `/1.1/users/<user_id>/forwards`

* SIP endpoint: `allow` and `disallow` options are not split into multiple options anymore.
* SCCP endpoint: `allow` and `disallow` options are not split into multiple options anymore.


16.04
-----

* The `summary` view has been added to `/users` (GET `/users?view=summary`)

* A new API for user's services has been added:

  * GET `/1.1/users/<user_id>/services`
  * GET `/1.1/users/<user_id>/services/<service_name>`
  * PUT `/1.1/users/<user_id>/services/<service_name>`

* A new API for user's forwards has been added:

  * GET `/1.1/users/<user_id>/forwards`
  * GET `/1.1/users/<user_id>/forwards/<forward_name>`
  * PUT `/1.1/users/<user_id>/forwards/<forward_name>`

* GET `/1.1/users/export` now requires the following header for CSV output::

   Accept: text/csv; charset=utf-8

* Added call permissions endpoints:

  * GET `/1.1/callpermissions`
  * POST `/1.1/callpermissions`
  * GET `/1.1/callpermissions/<callpermission_id>`
  * PUT `/1.1/callpermissions/<callpermission_id>`
  * DELETE `/1.1/callpermissions/<callpermission_id>`


16.03
-----

* Added switchboard endpoints:

  * GET `/1.1/switchboards`
  * GET `/1.1/switchboards/<switchboard_id>/stats`

* A new API for associating a line with a device has been added:

  * PUT `/1.1/lines/<line_id>/devices/<device_id>`
  * DELETE `/1.1/lines/<line_id>/devices/<device_id>`

* The following URLs have been deleted. Please use the new API instead:

  * GET `/1.1/devices/<device_id>/associate_line/<line_id>`
  * GET `/1.1/devices/<device_id>/dissociate_line/<line_id>`


16.02
-----

* Added users endpoints in REST API:

  * GET `/1.1/users/<user_uuid>/lines/main/associated/endpoints/sip`


16.01
-----

* The SIP API has been improved. `options` now accepts any extra parameter.  However, due to
  certain database limitations, parameters that appear in changelog 15.17 may only
  appear once in the list. This limitation will be removed in future versions.
* A new API for custom endpoints has been added: `/1.1/endpoints/custom`
* A new API for associating custom endpoints has been added: `/1.1/lines/<line_id>/endpoints/custom/<endpoint_id>`


15.20
-----

* A new API for mass updating users has been added: PUT `/1.1/users/import`
* A new API for exporting users has been added: GET `/1.1/users/export`


15.19
-----

* A new API for mass importing users has been added: POST `/1.1/users/import`
* The following fields have been added to the `/users` API:

  * supervision_enabled
  * call_tranfer_enabled
  * ring_seconds
  * simultaneous_calls


15.18
-----

* Ports 50050 and 50051 have been removed. Please use 9486 and 9487 instead
* Added sccp endpoints in REST API:

  * GET `/1.1/endpoints/sccp`
  * POST `/1.1/endpoints/sccp`
  * DELETE `/1.1/endpoints/sccp/<sccp_id>`
  * GET `/1.1/endpoints/sccp/<sccp_id>`
  * PUT `/1.1/endpoints/sccp/<sccp_id>`
  * GET `/1.1/endpoints/sccp/<sccp_id>/lines`
  * GET `/1.1/lines/<line_id>/endpoints/sccp`
  * DELETE `/1.1/lines/<line_id>/endpoints/sccp/<sccp_id>`
  * PUT `/1.1/lines/<line_id>/endpoints/sccp/<sccp_id>`

* Added lines endpoints in REST API:

  * GET `/1.1/lines/<line_id>/users`


15.17
-----

* A new API for SIP endpoints has been added. Consult the documentation
  on http://api.wazo.community for further details.
* The `/lines_sip` API has been deprecated. Please use `/lines` and `/endpoints/sip` instead.
* Due to certain limitations in the database, only a limited number of
  optional parameters can be configured. This limitation will be removed
  in future releases. Supported parameters are listed further down.
* Certain fields in the `/lines` API have been modified. List
  of fields are further down


Fields modified in the `/lines` API
-----------------------------------

| Name                   | Replaced by       | Editable ? | Required ? |
|------------------------|-------------------|------------|------------|
| id                     |                   | no         |            |
| device_id              |                   | no         |            |
| name                   |                   | no         |            |
| protocol               |                   | no         |            |
| device_slot            | position          | no         |            |
| provisioning_extension | provisioning_code | no         |            |
| context                |                   | yes        | yes        |
| provisioning_code      |                   | yes        |            |
| position               |                   | yes        |            |
| caller_id_name         |                   | yes        |            |
| caller_id_num          |                   | yes        |            |


.. _sip-endpoint-parameters:

Supported parameters on SIP endpoints
-------------------------------------

 * md5secret
 * language
 * accountcode
 * amaflags
 * allowtransfer
 * fromuser
 * fromdomain
 * subscribemwi
 * buggymwi
 * call-limit
 * callerid
 * fullname
 * cid-number
 * maxcallbitrate
 * insecure
 * nat
 * promiscredir
 * usereqphone
 * videosupport
 * trustrpid
 * sendrpid
 * allowsubscribe
 * allowoverlap
 * dtmfmode
 * rfc2833compensate
 * qualify
 * g726nonstandard
 * disallow
 * allow
 * autoframing
 * mohinterpret
 * useclientcode
 * progressinband
 * t38pt-udptl
 * t38pt-usertpsource
 * rtptimeout
 * rtpholdtimeout
 * rtpkeepalive
 * deny
 * permit
 * defaultip
 * setvar
 * port
 * regexten
 * subscribecontext
 * vmexten
 * callingpres
 * parkinglot
 * protocol
 * outboundproxy
 * transport
 * remotesecret
 * directmedia
 * callcounter
 * busylevel
 * ignoresdpversion
 * session-timers
 * session-expires
 * session-minse
 * session-refresher
 * callbackextension
 * timert1
 * timerb
 * qualifyfreq
 * contactpermit
 * contactdeny
 * unsolicited_mailbox
 * use-q850-reason
 * encryption
 * snom-aoc-enabled
 * maxforwards
 * disallowed-methods
 * textsupport


15.16
-----

* The parameter `skip` is now deprecated. Use `offset` instead for:

  * `GET /1.1/devices`
  * `GET /1.1/extensions`
  * `GET /1.1/voicemails`
  * `GET /1.1/users`

* The users resource can be referred to by `uuid`

  * `GET /1.1/users/<uuid>`
  * `PUT /1.1/users/<uuid>`
  * `DELETE /1.1/users/<uuid>`


15.15
-----

 * The field `enabled` has been added to the voicemail model
 * A line is no longer required when associating a voicemail with a user
 * Voicemails can now be edited even when they are associated to a user


15.14
-----

 * All optional fields on a user are now always null (sometimes they were empty strings)
 * The caller id is no longer automatically updated when the firstname or lastname is modified. You must update the
   caller id yourself if you modify the user's name.
 * Caller id will be generated if and only if it does not exist when creating a user.


14.16
-----

* Association user-voicemail, when associating a voicemail whose id does not exist:

  * before: error 404
  * after: error 400


14.14
-----

* Association line-extension, a same extension can not be associated to multiple lines


14.13
-----

* Resource line, field `provisioning_extension`: type changed from `int` to `string`
