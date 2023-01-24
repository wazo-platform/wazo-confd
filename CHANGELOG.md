# Changelog

## IN PROGRESS

* PUT on `/users?recursive=true` added, to provide a way to update fallbacks and forwards for a specific user.

## 23.01

* Bus configuration keys changes:

  * key `exchange_name` now defaults to `wazo-headers`
  * key `exchange_type` removed
  * key `exchange_durable` removed
  * key `subscribe_exchange_name` removed

## 22.17

* DELETE on `/users?recursive=true` added, to provide a way to delete a user and their related resources.
* `/users` endpoint now create the voicemail if it is specified in the body and associates it to the user.
* `/users` endpoint now associates the voicemail if it is specified in the body.
* `/users` endpoint now associates forwards if specified in the body.
* `/users` endpoint now associates fallbacks if specified in the body.
* `/users` endpoint now associates an unallocated device if specified in the body.
* `/users` endpoint now create the agent if it is specified in the body and associates it to the user.
* The following resource has been added:

  * POST `/1.1/users/<user_id>/voicemails`

## 22.16

* POST on `/users` can now create a user and all their related resources.

## 22.15

* PUT on `/users/<user_id>/groups` now accepts the group `uuid` as well as the group `id` in its body
* The `/tenants` endpoints were modified to remove the field `webrtc_video_sip_template_uuid`.
* `/lines` endpoint now create the SIP, SCCP or custom endpoint if it is specified in the body and associates it to the line.
* `/lines` endpoint now create the extension if it is specified in the body and associates it to the line.

## 22.14

* `/wizard` endpoint updates now the configuration file for autoprovisionning `/etc/asterisk/pjsip.d/05-autoprov-wizard.conf` with the `language` value it receives in the request body. However, if the user wants to change the language used for audio provisionning; they will have to do it manually for now.

## 22.13

* `/status` endpoint has now been included into `wazo-confd`, and it returns the current status (`ok` or `fail`) of the following:
  * `master_tenant`
  * `bus_consumer`
  * `service_token`
  * `rest_api`

* The following resource has been added:

  * POST `/1.1/lines/<line_id>/extensions`

* It is now possible to delete a user without dissociating the line first

* The following event's name have been changed to avoid name collision:

  * plugin `call_filter_users`:

    * `users_associated` to `call_filter_surrogate_users_associated`
    * `users_associated` to `call_filter_recipient_users_associated`

  * plugin `call_pickup_members`:

    * `users_associated` to `call_pickup_interceptor_users_associated`
    * `users_associated` to `call_pickup_target_users_associated`
    * `groups_associated` to `call_pickup_interceptor_groups_associated`
    * `groups_associated` to `call_pickup_target_groups_associated`

  * plugin `group_call_permission`:

    * `call_permission_associated` to `group_call_permission_associated`
    * `call_permission_dissocated` to `group_call_permission_dissociated`

  * plugin `group_member`:

    * `users_associated` to `group_member_users_associated`
    * `extensions_associated` to `group_member_extensions_associated`

  * plugin `outcall_call_permission`:

    * `call_permission_associated` to `outcall_call_permission_associated`
    * `call_permission_dissociated` to `outcall_call_permission_dissociated`

  * plugin `outcall_trunk`:

    * `trunks_associated` to `outcall_trunk_associated`

## 22.09

* The following resources has been added:

  * GET `/1.1/users/subscriptions`

## 22.06

* Meeting authorizations are now only valid for 24 hours. They are automatically
  deleted after 24 hours.

## 22.05

* The following resources have been added:

  * `GET /users/me/meetings/<meeting_uuid>/authorizations`
  * `GET, DELETE /users/me/meetings/<meeting_uuid>/authorizations/<authorization_uuid>`
  * `PUT /users/me/meetings/<meeting_uuid>/authorizations/<authorization_uuid>/accept`
  * `PUT /users/me/meetings/<meeting_uuid>/authorizations/<authorization_uuid>/reject`
  * `POST /guests/<guest_uuid>/meetings/<meeting_uuid>/authorizations`
  * `GET /guests/<guest_uuid>/meetings/<meeting_uuid>/authorizations/<authorization_uuid>`

* the `meeting` resource now has a `require_authorization` field.

## 22.01

* the `meeting` resource now has a `creation_time` read only field.
* the `meeting` resource now has a read only `exten` field.

## 21.16

* the `meeting` resource now has a `persistent` field.

## 21.15

* A music on hold now has a read-only auto-generated `name` and a required `label` instead
  of a user-provided `name` and optional `label`. For compatibility purposes, if a music
  on hold is created using only a `name`, it will be used as the `label` and
  auto-generated.

## 21.14

* The following resources have been added:

  * `GET, POST /ingresses/http`
  * `GET, PUT, DELETE /ingresses/http/<ingress_http_uuid>`

## 21.13

* The following resources have been added:

  * `GET, POST /meetings`
  * `GET, PUT, DELETE /meetings/<meeting_uuid>`
  * `GET, POST /users/me/meetings`
  * `GET, PUT, DELETE /users/me/meetings/<meeting_uuid>`
  * `GET /guests/me/meetings`

## 21.12

* The surrogates user list of `callfilters` resource now implements the `exten` field
* The following query string parameters have been added to GET `/1.1/sounds`:

  * `search`
  * `order`
  * `limit`
  * `offset`
  * `direction`

* The following resources have been added:

  * GET, PUT `/1.1/switchboards/<switchboard_uui>/fallbacks`

## 21.10

* The name of `call_permissions` is now unique to a given tenant only

## 21.09

* The `user` destination type can now include a `moh_uuid` which will be used instead of the
  ringback tone. This includes the following resources

  * call_filter fallbacks
  * group fallbacks
  * incall destinations
  * ivr destinations
  * queue fallbacks
  * schedule closed destinations
  * user fallbacks

## 21.08

* The `switchboards` resource now implements the following fields:

  * `waiting_room_music_on_hold`
  * `queue_music_on_hold`

## 21.04

* The following resources have been added:

  * GET, PUT, DELETE `/1.1/groups/<group_uuid>`
  * PUT, DELETE `/1.1/groups/<group_uuid>/extensions/<extension_id>`
  * PUT, DELETE `/1.1/groups/<group_uuid>/schedules/<schedule_id>`
  * PUT, DELETE `/1.1/groups/<group_uuid>/fallbacks`
  * PUT `/1.1/groups/<group_uuid>/members/users`
  * PUT `/1.1/groups/<group_uuid>/members/extensions`
  * GET, PUT `/1.1/emails`

* The following resources have been deprecated:

  * GET, PUT, DELETE `/1.1/groups/<group_id>`
  * PUT, DELETE `/1.1/groups/<group_id>/extensions/<extension_id>`
  * PUT, DELETE `/1.1/groups/<group_id>/schedules/<schedule_id>`
  * PUT, DELETE `/1.1/groups/<group_id>/fallbacks`
  * PUT `/1.1/groups/{group_id}/members/users`
  * PUT `/1.1/groups/{group_id}/members/extensions`

## 21.03

* The following endpoints have been restricted to the master tenant only:

  * GET `/1.1/access_features`
  * POST `/1.1/access_features`
  * DELETE `/1.1/access_features/<access_feature_id>`
  * GET `/1.1/access_features/<access_feature_id>`
  * PUT `/1.1/access_features/<access_feature_id>`
  * GET `/1.1/asterisk/confbridge/wazo_default_bridge`
  * PUT `/1.1/asterisk/confbridge/wazo_default_bridge`
  * GET `/1.1/asterisk/confbridge/wazo_default_user`
  * PUT `/1.1/asterisk/confbridge/wazo_default_user`
  * GET `/1.1/asterisk/features/applicationmap`
  * PUT `/1.1/asterisk/features/applicationmap`
  * GET `/1.1/asterisk/features/featuremap`
  * PUT `/1.1/asterisk/features/featuremap`
  * GET `/1.1/asterisk/features/general`
  * PUT `/1.1/asterisk/features/general`
  * GET `/1.1/asterisk/hep/general`
  * PUT `/1.1/asterisk/hep/general`
  * GET `/1.1/asterisk/iax/callnumberlimits`
  * PUT `/1.1/asterisk/iax/callnumberlimits`
  * GET `/1.1/asterisk/iax/general`
  * PUT `/1.1/asterisk/iax/general`
  * GET `/1.1/asterisk/pjsip/doc`
  * GET `/1.1/asterisk/pjsip/global`
  * PUT `/1.1/asterisk/pjsip/global`
  * GET `/1.1/asterisk/pjsip/system`
  * PUT `/1.1/asterisk/pjsip/system`
  * GET `/1.1/asterisk/queues/general`
  * PUT `/1.1/asterisk/queues/general`
  * GET `/1.1/asterisk/rtp/general`
  * PUT `/1.1/asterisk/rtp/general`
  * GET `/1.1/asterisk/rtp/ice_host_candidates`
  * PUT `/1.1/asterisk/rtp/ice_host_candidates`
  * GET `/1.1/asterisk/sccp/general`
  * PUT `/1.1/asterisk/sccp/general`
  * GET `/1.1/asterisk/voicemail/general`
  * PUT `/1.1/asterisk/voicemail/general`
  * GET `/1.1/asterisk/voicemail/zonemessages`
  * PUT `/1.1/asterisk/voicemail/zonemessages`
  * GET `/1.1/configuration/live_reload`
  * PUT `/1.1/configuration/live_reload`
  * GET `/1.1/dhcp`
  * PUT `/1.1/dhcp`
  * GET `/1.1/extensions/features`
  * GET `/1.1/extensions/features/<extension_id>`
  * PUT `/1.1/extensions/features/<extension_id>`
  * GET `/1.1/ha`
  * PUT `/1.1/ha`
  * GET `/1.1/provisioning/networking`
  * PUT `/1.1/provisioning/networking`
  * POST `/1.1/sip/transports`
  * PUT `/1.1/sip/transports/<transport_uuid>`
  * DELETE `/1.1/sip/transports/<transport_uuid>`
  * GET `/1.1/registrars`
  * POST `/1.1/registrars`
  * GET `/1.1/registrars/<registrar_uuid>`
  * PUT `/1.1/registrars/<registrar_uuid>`
  * DELETE `/1.1/registrars/<registrar_uuid>`

## 21.01

* New parameters have been added to the users resource, including import/export:

  * `call_record_outgoing_external_enabled`
  * `call_record_outgoing_internal_enabled`
  * `call_record_incoming_external_enabled`
  * `call_record_incoming_internal_enabled`

* The following user parameter has been deprecated:

  * `call_record_enabled`

* The following user parameter has been removed from users import/export:

  * `call_record_enabled`

* Removed `meetme` destination type for fallbacks, schedules, queues, incalls and ivr.
* Undeprecate `conference` function key

## 20.16

* The following resources have been added:

  * GET `/1.1/users/<uuid>/voicemails`

## 20.15

* The following resources have been added:

  * GET `/1.1/external/apps`
  * POST `/1.1/external/apps/<app_name>`
  * GET `/1.1/external/apps/<app_name>`
  * PUT `/1.1/external/apps/<app_name>`
  * DELETE `/1.1/external/apps/<app_name>`
  * GET `/1.1/users/<user_uuid>/external/apps`
  * POST `/1.1/users/<user_uuid>/external/apps/<app_name>`
  * GET `/1.1/users/<user_uuid>/external/apps/<app_name>`
  * PUT `/1.1/users/<user_uuid>/external/apps/<app_name>`
  * DELETE `/1.1/users/<user_uuid>/external/apps/<app_name>`

## 20.14

* Add the following resources

  * GET `/1.1/tenants`
  * GET `/1.1/tenants/<tenant_uuid>`

## 20.13

* The body of `/1.1/endpoints/sip` has been modified to be used with PJSIP
* The following resources have been removed:

  * `/1.1/registers/sip/<register_id>`
  * `/1.1/registers/sip`
  * `/1.1/trunks/<trunk_id>/registers/sip/<register_id>`
  * `/1.1/asterisk/sip/general`

* The identifier of `/1.1/endpoints/sip` is now a UUID
* The following resources have been added:

  * GET `/1.1/endpoints/sip/templates`
  * POST `/1.1/endpoints/sip/templates`
  * GET `/1.1/endpoints/sip/templates/<template_uuid>`
  * PUT `/1.1/endpoints/sip/templates/<template_uuid>`
  * DELETE `/1.1/endpoints/sip/templates/<template_uuid>`

## 20.11

* The following endpoints are now multi-tenant.

  This means that created resources will be in the same tenant as the creator or in the tenant
  specified by the Wazo-Tenant HTTP header. Listing resources will also only list the ones in the
  user's tenant unless a sub-tenant is specified using the Wazo-Tenant header. The `recurse=true`
  query string can be used to list from multiple tenants. GET, DELETE and PUT on a resource that is
  not tenant accessible will result in a 404. New readonly parameter has also been added:
  `tenant_uuid`.

  * POST `/1.1/funckeys/templates`
  * GET `/1.1/funckeys/templates`
  * GET `/1.1/funckeys/templates/<template_id>`
  * PUT `/1.1/funckeys/templates/<template_id>`
  * DELETE `/1.1/funckeys/templates/<template_id>`

  * GET `/1.1/funckeys/templates/<template_id>/<position>`
  * PUT `/1.1/funckeys/templates/<template_id>/<position>`
  * DELETE `/1.1/funckeys/templates/<template_id>/<position>`

  * GET `/1.1/funckeys/templates/<template_id>/users`
  * GET `/1.1/users/<user_uuid>/funckeys`
  * PUT `/1.1/users/<user_uuid>/funckeys`

  * GET `/1.1/users/<user_uuid>/funckeys/<position>`
  * PUT `/1.1/users/<user_uuid>/funckeys/<position>`
  * DELETE `/1.1/users/<user_uuid>/funckeys/<position>`

  * GET `/1.1/users/<user_uuid>/funckeys/templates`
  * PUT `/1.1/users/<user_uuid>/funckeys/templates/<template_id>`
  * DELETE `/1.1/users/<user_uuid>/funckeys/templates/<template_id>`

## 20.09

* The `rest_host` and `rest_https_port` fields have been removed from the
  `/1.1/provisioning/networking` resource.

## 20.07

* Deprecate SSL configuration
* A new parameter has been added to the incalls resource:

  * `greeting_sound`

* The following deprecated endpoints are removed.

  * GET `/1.1/callpermissions/<call_permission_id>/users`
  * GET `/1.1/users/<user_uuid>/callpermissions`

  * GET `/1.1/endpoints/custom/<endpoint_id>/lines`
  * GET `/1.1/endpoints/sccp/<endpoint_id>/lines`
  * GET `/1.1/endpoints/sip/<endpoint_id>/lines`
  * GET `/1.1/lines/<line_id>/endpoints/custom`
  * GET `/1.1/lines/<line_id>/endpoints/sccp`
  * GET `/1.1/lines/<line_id>/endpoints/sip`

  * GET `/1.1/endpoints/custom/<endpoint_id>/trunks`
  * GET `/1.1/endpoints/sip/<endpoint_id>/trunks`
  * GET `/1.1/trunks/<line_id>/endpoints/custom`
  * GET `/1.1/trunks/<line_id>/endpoints/sip`

  * GET `/1.1/lines_sip`
  * POST `/1.1/lines_sip`
  * DELETE `/1.1/lines_sip/<line_id>`
  * GET `/1.1/lines_sip/<line_id>`
  * PUT `/1.1/lines_sip/<line_id>`

  * GET `/1.1/extensions/<extension_id>/lines`
  * GET `/1.1/lines/<line_id>/extensions`
  * POST `/1.1/lines/<line_id>/extensions`

  * GET `/1.1/extensions/<extension_id>/line`
  * GET `/1.1/lines/<line_id>/extension`
  * POST `/1.1/lines/<line_id>/extension`
  * DELETE `/1.1/lines/<line_id>/extension`

  * GET `/1.1/users/<user_id>/lines`
  * GET `/1.1/lines/<line_id>/users`
  * POST `/1.1/lines/<line_id>/users`

  * POST `/1.1/queues/<queue_id>/members/agents`
  * GET `/1.1/queues/<queue_id>/members/agents/<agent_id>`

  * GET `/1.1/users/<user_id>/agents`

  * GET `/1.1/users/<user_id>/voicemails`
  * GET `/1.1/voicemails/<voicemail_id>/users`

  * GET `/1.1/users/<user_id>/voicemail`
  * POST `/1.1/users/<user_id>/voicemail`
  * DELETE `/1.1/users/<user_id>/voicemail`

## 20.05

* `/1.1/users/import` now accepts `webrtc` in the `line_protocol` column
* Add the following resources

  * POST `/1.1/sip/transports`
  * GET `/1.1/sip/transports`
  * GET `/1.1/sip/transports/{transport_uuid}`
  * PUT `/1.1/sip/transports/{transport_uuid}`
  * DELETE `/1.1/sip/transports/{transport_uuid}`

## 20.04

* Add the following resources

  * GET `/1.1/asterisk/pjsip/global`
  * GET `/1.1/asterisk/pjsip/system`

* A new `mark_answered_elsewhere` parameter has been added to the groups and queues resources

## 20.03

* Add the following resources

  * GET `/1.1/asterisk/pjsip/doc`

* The `subscription_type` field is now available in the following resources

  * POST `/1.1/users/import`
  * GET `/1.1/users/export`

## 20.02

* The GET on `1.1/wizard` now returns the `configurable` and `configurable_status` fields

## 20.01

* The voicemail `name` no longer changes according to the user `firstname`/`lastname`

## 19.18

* A new read-only parameter has been added to the users resource:

  * `call_pickup_target_users`

## 19.17

* Legacy search parameter with `q` has been removed from user resource
* Deprecated `skip` option has been removed from resource list

## 19.16

* Search with the `search` parameter is now accent insensitive
* Trunk and Line resources now includes the `name` in the `endpoint_sip` relation

## 19.15

* The POST `/1.1/endpoints/sip` now accepts a `name` and a `username` field. If
  you relied on the behavior that copied to `username` to the `name` field you must
  upgrade your software before that compatibility layer gets removed in a future version.

## 19.13

* A new API for configuring features access has been added:

  * GET `/1.1/access_features`
  * POST `/1.1/access_features`
  * GET `/1.1/access_features/<access_feature_id>`
  * PUT `/1.1/access_features/<access_features_id>`
  * DELETE `/1.1/access_features/<access_feature_id>`

## 19.12

* The API `/1.1/call_logs` for call logs have been removed

## 19.11

* A new API for configuring the provisioning registrars has been added:

  * GET `/1.1/registrars`
  * POST `/1.1/registrars`
  * GET `/1.1/registrars/<registrar_id>`
  * PUT `/1.1/registrars/<registrar_id>`
  * DELETE `/1.1/registrars/<registrar_id>`

## 19.10

* A new API for associating a line with an application has been added:

  * PUT `/1.1/lines/<line_id>/applications/<application_id>`
  * DELETE `/1.1/lines/<line_id>/applications/<application_id>`

* For newly created applications with `node` destination, calls are not
  automatically answered anymore. A new `answer` parameter has been
  added in `destination_options` to configure the answer behavior of the node.

## 19.08

* Due to the removal of the Wazo Client QT, the following endpoints has been deleted:
  * GET `/1.1/cti_profiles`
  * GET `/1.1/cti_profiles/<cti_profile_id>`
  * GET `/1.1/users/<user_uuid>/cti`
  * PUT `/1.1/users/<user_uuid>/cti`
  Also note that endpoints `/users` don't have `cti_profile` parameter anymore.

## 19.07

* The following endpoints are now multi-tenant.

  This means that created resources will be in the same tenant as the creator or in the tenant
  specified by the Wazo-Tenant HTTP header. Listing resources will also only list the ones in the
  user's tenant unless a sub-tenant is specified using the Wazo-Tenant header. The `recurse=true`
  query string can be used to list from multiple tenants. GET, DELETE and PUT on a resource that is
  not tenant accessible will result in a 404. New readonly parameter has also been added:
  `tenant_uuid`.

  * `/1.1/queues/skillrules`

* Added Unallocated devices endpoints:
  * GET `/1.1/devices/unallocated`
  * PUT `/1.1/devices/unallocated/<device_id>`

* The following endpoints are now multi-tenant.

  This means that created resources will be in the same tenant as the creator or in the tenant
  specified by the Wazo-Tenant HTTP header. Listing resources will also only list the ones in the
  user's tenant unless a sub-tenant is specified using the Wazo-Tenant header. The `recurse=true`
  query string can be used to list from multiple tenants. GET, DELETE and PUT on a resource that is
  not tenant accessible will result in a 404. New readonly parameter has also been added:
  `tenant_uuid`.

  * `/1.1/agents/skills`

## 19.06

* The `http` configuration section has been removed. Also the `https` section has moved to
  `rest_api` to be similar with other daemons.
* The `/1.1/users/import` PUT has been disabled since it creates invalid configurations
* The `/1.1/users/export` resource will now only list users from the specified tenant.

* The following endpoints are now multi-tenant.

  This means that created resources will be in the same tenant as the creator or in the tenant
  specified by the Wazo-Tenant HTTP header. Listing resources will also only list the ones in the
  user's tenant unless a sub-tenant is specified using the Wazo-Tenant header. The `recurse=true`
  query string can be used to list from multiple tenants. GET, DELETE and PUT on a resource that is
  not tenant accessible will result in a 404. New readonly parameter has also been added:
  `tenant_uuid`.

  * `/1.1/agents`

## 19.05

* The following endpoints are now multi-tenant.

  This means that created resources will be in the same tenant as the creator or in the tenant
  specified by the Wazo-Tenant HTTP header. Listing resources will also only list the ones in the
  user's tenant unless a sub-tenant is specified using the Wazo-Tenant header. The `recurse=true`
  query string can be used to list from multiple tenants. GET, DELETE and PUT on a resource that is
  not tenant accessible will result in a 404. New readonly parameter has also been added:
  `tenant_uuid`.

  * `/1.1/queues`
  * `/1.1/switchboards`

* Added Provisioning Networking Configuration endpoints:

  * GET `/1.1/provisioning/networking`
  * PUT `/1.1/provisioning/networking`

* New readonly parameters have been added to the device resource:

  * `is_new`

* The `cti_profile_name`, `cti_profile_enabled` and `entity` fields have been removed from the `/1.1/users/import` resource.
* The `/1.1/users/import` will now create the users in the creator's tenant or the specified tenant.
* The `/1.1/user/<user_id>/entities` resource has been removed.
* The `/1.1/entities` resource has been removed.
* The `summary` view does not return the entity anymore.
* The following fields have been removed from the `/1.1/wizard` POST body

  * `entity_name`
  * `context_outcall`
  * `context_incall`
  * `context_internal`

* The following steps have been removed from the `/1.1/wizard` POST body

  * `phonebook`
  * `tenant`

* In `/dhcp`, the field `extra_network_interfaces` is renamed to `network_interfaces`.
* A new function key type has been added: `groupmember`

## 19.04

* New readonly parameters have been added to the funckeys resource:

  * For destinations of type `bsfilter`:

    * `filter_member_firstname`
    * `filter_member_lastname`

* New readonly parameters have been added to the call filter surrogate resource:

  * `member_id`

* The following endpoints are now multi-tenant.

  This means that created resources will be in the same tenant as the creator or in the tenant
  specified by the Wazo-Tenant HTTP header. Listing resources will also only list the ones in the
  user's tenant unless a sub-tenant is specified using the Wazo-Tenant header. The `recurse=true`
  query string can be used to list from multiple tenants. GET, DELETE and PUT on a resource that is
  not tenant accessible will result in a 404. New readonly parameter has also been added:
  `tenant_uuid`.

  * `/1.1/callpickups`
  * `/1.1/devices`

## 19.03

* The following endpoints are now multi-tenant.

  This means that created resources will be in the same tenant as the creator or in the tenant
  specified by the Wazo-Tenant HTTP header. Listing resources will also only list the ones in the
  user's tenant unless a sub-tenant is specified using the Wazo-Tenant header. The `recurse=true`
  query string can be used to list from multiple tenants. GET, DELETE and PUT on a resource that is
  not tenant accessible will result in a 404. New readonly parameter has also been added:
  `tenant_uuid`.

  * `/1.1/sounds`

* Added DHCP endpoints:

  * GET `/1.1/dhcp`
  * PUT `/1.1/dhcp`

* Added High Availability endpoints:

  * GET `/1.1/ha`
  * PUT `/1.1/ha`

## 19.02

* The following endpoints are now multi-tenant.

  This means that created resources will be in the same tenant as the creator or in the tenant
  specified by the Wazo-Tenant HTTP header. Listing resources will also only list the ones in the
  user's tenant unless a sub-tenant is specified using the Wazo-Tenant header. The `recurse=true`
  query string can be used to list from multiple tenants. GET, DELETE and PUT on a resource that is
  not tenant accessible will result in a 404. New readonly parameter has also been added:
  `tenant_uuid`.

  * `/1.1/schedules`
  * `/1.1/ivr`

## 19.01

* New steps parameter have been added to the wizard resource:

  * `admin`

## 18.14

* New readonly parameters have been added to the agent resource:

  * `users`

## 18.13

* The following URLs have been deprecated:

  * GET `/1.1/endpoints/custom/<custom_id>/lines`
  * GET `/1.1/endpoints/sccp/<custom_id>/lines`
  * GET `/1.1/endpoints/sip/<custom_id>/lines`
  * GET `/1.1/lines/<line_id>/endpoints/custom`
  * GET `/1.1/lines/<line_id>/endpoints/sccp`
  * GET `/1.1/lines/<line_id>/endpoints/sip`

  * GET `/1.1/endpoints/custom/<custom_id>/trunks`
  * GET `/1.1/endpoints/sip/<custom_id>/trunks`
  * GET `/1.1/trunks/<trunk_id>/endpoints/custom`
  * GET `/1.1/trunks/<trunk_id>/endpoints/sip`

  * GET `/1.1/lines/<line_id>/extensions`
  * GET `/1.1/extensions/<extension_id>/lines`

  * GET `/1.1/callpermissions/<call_permission_id>/users`
  * GET `/1.1/users/<user_id>/callpermissions`

  * GET `/1.1/lines/<line_id>/users`
  * GET `/1.1/users/<user_id>/lines`

  * GET `/1.1/users/<user_id>/voicemails`
  * GET `/1.1/voicemails/<voicemail_id>/users`

  * GET `/1.1/users/<user_id>/agent`
  * GET `/1.1/users/<user_id>/cti`
  * GET `/1.1/users/<user_id>/entities`

  * POST `/1.1/entities`
  * GET `/1.1/entities`
  * GET `/1.1/entities/<entity_id>`
  * PUT `/1.1/entities/<entity_id>`
  * DELETE `/1.1/entities/<entity_id>`

## 18.10

* Added applications endpoints:

  * GET `/1.1/applications`
  * POST `/1.1/applications`
  * DELETE `/1.1/applications/<application_uuid>`
  * GET `/1.1/applications/<application_uuid>`
  * PUT `/1.1/applications/<application_uuid>`

* New destination application type:

  * For destinations of type `application`:

    * `custom`

* New parameter have been added to the wizard resource:

  * `steps`

## 18.09

* Added RTP general endpoints:

  * GET `/1.1/asterisk/rtp/general`
  * PUT `/1.1/asterisk/rtp/general`

* Added RTP ice host candidates endpoints:

  * GET `/1.1/asterisk/rtp/ice_host_candidates`
  * PUT `/1.1/asterisk/rtp/ice_host_candidates`

* Added queues general endpoints:

  * GET `/1.1/asterisk/queues/general`
  * PUT `/1.1/asterisk/queues/general`

* The following endpoints are now multi-tenant.

  This means that created resources will be in the same tenant as the creator or in the tenant
  specified by the Wazo-Tenant HTTP header. Listing resources will also only list the ones in the
  user's tenant unless a sub-tenant is specified using the Wazo-Tenant header. The `recurse=true`
  query string can be used to list from multiple tenants. GET, DELETE and PUT on a resource that is
  not tenant accessible will result in a 404. New readonly parameter has also been added:
  `tenant_uuid`.

  * `/callfilters`
  * `/callpermissions`
  * `/endpoints/custom`
  * `/endpoints/iax`
  * `/endpoints/sccp`
  * `/endpoints/sip`
  * `/pagings`
  * `/parkinglots`
  * `/trunks`

## 18.08

* Added queue skill rule endpoints:

  * GET `/1.1/queues/skillrules`
  * POST `/1.1/queues/skillrules`
  * DELETE `/1.1/queues/skillrules/<skill_rule_id>`
  * GET `/1.1/queues/skillrules/<skill_rule_id>`
  * PUT `/1.1/queues/skillrules/<skill_rule_id>`

* A new API for associating a agent with a skill has been added:

  * PUT `/1.1/agents/<agent_id>/skills/<skill_id>`
  * DELETE `/1.1/agents/<agent_id>/skills/<skill_id>`

* Added agent skill endpoints:

  * GET `/1.1/agents/skills`
  * POST `/1.1/agents/skills`
  * DELETE `/1.1/agents/skills/<skill_id>`
  * GET `/1.1/agents/skills/<skill_id>`
  * PUT `/1.1/agents/skills/<skill_id>`

* The following endpoints are now multi-tenant.

  This means that created resources will be in the same tenant as the creator or in the tenant
  specified by the Wazo-Tenant HTTP header. Listing resources will also only list the ones in the
  user's tenant unless a sub-tenant is specified using the Wazo-Tenant header. The `recurse=true`
  query string can be used to list from multiple tenants. GET, DELETE and PUT on a resource that is
  not tenant accessible will result in a 404. New readonly parameter has also been added:
  `tenant_uuid`.

  * `/outcalls`
  * `/groups`
  * `/incalls`
  * `/conferences`
  * `/lines`

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
  * `skills`

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

## 18.07

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

## 18.06

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

## 18.05

* Added call pickup endpoints:

  * GET `/1.1/callpickups`
  * POST `/1.1/callpickups`
  * DELETE `/1.1/callpickups/<call_pickup_id>`
  * GET `/1.1/callpickups/<call_pickup_id>`
  * PUT `/1.1/callpickups/<call_pickup_id>`

## 18.04

* The `password` field has been removed from GET `/1.1/users/export`
* The `Wazo-Tenant` header can now be used when creating users in a given tenant.

  * POST `/1.1/users`
  * POST `/1.1/users/import`

* The users GET, PUT and DELETE are now filtered by tenant. xivo-confd will behave as if users from other tenants do not exist.

## 18.02

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

## 18.01

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

## 17.17

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

## 17.16

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

## 17.13

* A line that is associated to a device can now be deleted
* A new API for user's services has been added:

  * PUT `/1.1/users/<user_id>/services`

## 17.10

* A new API for associating lines with a user has been added:

  * PUT `/1.1/users/<user_uuid>/lines`

## 17.09

* A new API for associating groups with a user has been added:

  * PUT `/1.1/users/<user_uuid>/groups`

## 17.05

* New readonly parameters have been added to the user resource:

  * `agent`

## 17.03

* A new API for managing :abbr:`MOH (Music On Hold)`:

  * GET `/1.1/moh`
  * POST `/1.1/moh`
  * DELETE `/1.1/moh/<moh_id>`
  * GET `/1.1/moh/<moh_id>`
  * PUT `/1.1/moh/<moh_id>`
  * DELETE `/1.1/moh/<moh_id>/files/<filename>`
  * GET `/1.1/moh/<moh_id>/files/<filename>`
  * PUT `/1.1/moh/<moh_id>/files/<filename>`

## 17.02

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

## 17.01

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

## 16.16

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

## 16.14

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

## 16.13

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

## 16.12

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

## 16.11

* A new API for associating a user with an agent has been added:

  * DELETE `/1.1/users/<user_id>/agents`
  * GET `/1.1/users/<user_id>/agents`
  * PUT `/1.1/users/<user_id>/agents/<agent_id>`

* A new API to list lines associated to an extension

  * GET `/1.1/extensions/<extension_id>/lines`


* The following URLs have been deprecated. Please use the new API instead:

  * GET `/1.1/extensions/<extension_id>/line`

## 16.10

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

## 16.09

* Added entities endpoints:

  * GET `/1.1/entities`
  * POST `/1.1/entities`
  * GET `/1.1/entities/<entity_id>`
  * DELETE `/1.1/entities/<entity_id>`

* A new API for updating all user's funckeys

  * PUT `/1.1/users/<user_id>/funckeys`

* A new parameter have been added to the users resource:

  * `dtmf_hangup_enabled`

## 16.06

* A new API for initializing a Wazo (passing the wizard):

  * GET `/1.1/wizard`
  * POST `/1.1/wizard`
  * GET `/1.1/wizard/discover`

* A new API for associating a user with an entity has been added:

  * GET `/1.1/users/<user_id>/entities`
  * PUT `/1.1/users/<user_id>/entities/<entity_id>`

## 16.05

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

## 16.04

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

## 16.03

* Added switchboard endpoints:

  * GET `/1.1/switchboards`
  * GET `/1.1/switchboards/<switchboard_id>/stats`

* A new API for associating a line with a device has been added:

  * PUT `/1.1/lines/<line_id>/devices/<device_id>`
  * DELETE `/1.1/lines/<line_id>/devices/<device_id>`

* The following URLs have been deleted. Please use the new API instead:

  * GET `/1.1/devices/<device_id>/associate_line/<line_id>`
  * GET `/1.1/devices/<device_id>/dissociate_line/<line_id>`

## 16.02

* Added users endpoints in REST API:

  * GET `/1.1/users/<user_uuid>/lines/main/associated/endpoints/sip`

## 16.01

* The SIP API has been improved. `options` now accepts any extra parameter.  However, due to
  certain database limitations, parameters that appear in changelog 15.17 may only
  appear once in the list. This limitation will be removed in future versions.
* A new API for custom endpoints has been added: `/1.1/endpoints/custom`
* A new API for associating custom endpoints has been added: `/1.1/lines/<line_id>/endpoints/custom/<endpoint_id>`

## 15.20

* A new API for mass updating users has been added: PUT `/1.1/users/import`
* A new API for exporting users has been added: GET `/1.1/users/export`

## 15.19

* A new API for mass importing users has been added: POST `/1.1/users/import`
* The following fields have been added to the `/users` API:

  * supervision_enabled
  * call_tranfer_enabled
  * ring_seconds
  * simultaneous_calls

## 15.18

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

## 15.17

* A new API for SIP endpoints has been added. Consult the documentation
  on http://api.wazo.community for further details.
* The `/lines_sip` API has been deprecated. Please use `/lines` and `/endpoints/sip` instead.
* Due to certain limitations in the database, only a limited number of
  optional parameters can be configured. This limitation will be removed
  in future releases. Supported parameters are listed further down.
* Certain fields in the `/lines` API have been modified. List
  of fields are further down

### Fields modified in the `/lines` API

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

### Supported parameters on SIP endpoints

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

## 15.16

* The parameter `skip` is now deprecated. Use `offset` instead for:

  * `GET /1.1/devices`
  * `GET /1.1/extensions`
  * `GET /1.1/voicemails`
  * `GET /1.1/users`

* The users resource can be referred to by `uuid`

  * `GET /1.1/users/<uuid>`
  * `PUT /1.1/users/<uuid>`
  * `DELETE /1.1/users/<uuid>`

## 15.15

* The field `enabled` has been added to the voicemail model
* A line is no longer required when associating a voicemail with a user
* Voicemails can now be edited even when they are associated to a user

## 15.14

* All optional fields on a user are now always null (sometimes they were empty strings)
* The caller id is no longer automatically updated when the firstname or lastname is modified. You must update the
 caller id yourself if you modify the user's name.
* Caller id will be generated if and only if it does not exist when creating a user.

## 14.16

* Association user-voicemail, when associating a voicemail whose id does not exist:

  * before: error 404
  * after: error 400

## 14.14

* Association line-extension, a same extension can not be associated to multiple lines

## 14.13

* Resource line, field `provisioning_extension`: type changed from `int` to `string`
