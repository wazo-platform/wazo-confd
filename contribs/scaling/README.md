# Scaling wazo-confd

wazo-confd splits its work into two roles, selectable per process with the
repeatable `--role` option or the `roles` configuration key (a map of role
name to boolean — disable a role explicitly, e.g. `consumer: false`):

- `api`: serve the REST API (and register in Consul when service discovery is
  enabled)
- `consumer`: handle the events of the other services (tenant added or
  deleted, meeting ready)

The default is both roles in one process.

Only the `api` role scales. **Run the `consumer` role in exactly one
process**: each process with that role receives every event, so two of them
would create or remove the resources of a tenant twice.

`GET /1.1/status` only reports `bus_consumer` on a process with the `consumer`
role.

## Topology 1: all-in-one (default)

Nothing to do. One `wazo-confd` process runs both roles, as always.

## Topology 2: extra workers on the same host

Start additional API-only processes with the systemd template, using the
instance name as the port:

```sh
systemctl enable --now wazo-confd-worker@19486 wazo-confd-worker@29486
```

Workers are tied to the main unit (`PartOf=wazo-confd.service`): they stop and
restart with it. Each worker advertises its own port in Consul automatically
(`service_discovery.advertise_port` defaults to the real listening port).

nginx already routes the API through the `wazo-confd` upstream defined in
`/etc/nginx/conf.d/wazo-confd-upstream.conf`. To spread the traffic across
the workers, add one server line per worker and reload nginx:

```nginx
upstream wazo-confd {
    server 127.0.0.1:9486;    # main instance (both roles)
    server 127.0.0.1:19486;   # wazo-confd-worker@19486
    server 127.0.0.1:29486;   # wazo-confd-worker@29486
}
```

```sh
nginx -t && systemctl reload nginx
```

Only the requests going through nginx are spread: a service configured to
reach wazo-confd on `localhost:9486` always reaches the main instance. Point
it at `http://localhost/api/confd` (port 80, prefix `/api/confd`) instead.

Each process keeps its own pool of database connections: `rest_api.min_threads`
at all times, up to `rest_api.max_threads` plus 10 under load. Check the
total against the `max_connections` of PostgreSQL.

All instances share `/var/log/wazo-confd.log`. Per-instance streams are
available through journald (`journalctl -t wazo-confd-worker@19486`).

## Topology 3: containers

Run one container with the default roles and as many API-only replicas as
needed, behind any HTTP load balancer:

```yaml
services:
  confd:
    image: wazoplatform/wazo-confd
  confd-api:
    image: wazoplatform/wazo-confd
    command: wazo-confd --role api
    deploy:
      replicas: 3
```

Or split the roles completely: `wazo-confd --role consumer` in one container
(it handles the bus events and starts no HTTP server) and
`wazo-confd --role api` in N replicas.
