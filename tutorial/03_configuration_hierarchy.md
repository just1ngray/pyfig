# Configuration Hierarchy

The default config provides some reasonable defaults, but these settings are not going to be useful or valid
for all environments, deployments, etc. A configuration hierarchy is a list of partial configuration overrides
that should be applied to the default config.

Pyfig supports any number of configuration overrides, and applies them in descending priority order.

```yaml
db:
  host: localhost
  port: 1234
api: http://localhost:8080/api
tasks:
   - foo
   - bar
   - baz
```

The above config represents an example (default) config used by some fake application. It's configured to work
well for development since it targets local resources. However, when deploying to production it's necessary to
specify production-specific settings. Instead of duplicating the config and making the modifications, we can
instead just adjust the values of interest.

```yaml
api: https://example.com/api

# will override the default to:

db:
  host: localhost
  port: 1234
api: https://example.com/api
tasks:
   - foo
   - bar
   - baz
```

These overrides are applied at the lowest dictionary level; leaving the other dictionary keys untouched.

```yaml
db:
  port: 9999

# will override the default to:

db:
  host: localhost
  port: 9999
api: http://localhost:8080/api
tasks:
   - foo
   - bar
   - baz
```

Overriding a list with another list will override the entire list:

```yaml
tasks:
  - overridden

# will override the default to:

db:
  host: localhost
  port: 1234
api: http://localhost:8080/api
tasks:
   - overridden
```

But using a special override syntax, it is possible to override an element of a list by its index:

```yaml
tasks:
  1: index number 1 is the second element
  -1: even negative indexes work

# will override the default to

db:
  host: localhost
  port: 1234
api: http://localhost:8080/api
tasks:
   - foo
   - index number 1 is the second element
   - even negative indexes work
```

Multiple overrides can be specified, and they'll be applied in priority order. They can even override each other:

```yaml
# top level override
db:
  port: 444

# mid level override
db:
  host: https://mydb.hosted.com
  port: 433
api: https://example.com/api

# are combined with the default to:
db:
  host: https://mydb.hosted.com
  port: 444
api: https://example.com/api
tasks:
   - foo
   - bar
   - baz
```

In general, start with the default config, and then apply configuration overrides in ascending priority order until
all overriding configs have overwritten previous settings. The result will be your merged (unified) configuration.
