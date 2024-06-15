# Git Syncer Backend

## Usage

### Settings

Can be set by both yaml file and environment variables, [example](examples/settings.yaml).
Settings file path can be set by `GIT_SYNCER_SETTINGS_YAML` environment variable.

Settings consist of next sections:

- app - general application settings
- logs - logging settings
- scheduler - scheduler settings
- repos - list of repositories to sync

#### App

`app.env` - application environment, used mainly for logging. Default is `production`.

```yaml
app:
  env: development
```

Can be set by `GIT_SYNCER_APP__ENV` environment variable.

---

`app.debug` - debug mode, enables more verbose logging. Default is `false`.

```yaml
app:
  debug: true
```

Can be set by `GIT_SYNCER_APP__DEBUG` environment variable.

#### Logs

`logs.level` logging level, can be one of `debug`, `info`, `warning`, `error`. Default is `info`.

```yaml
logs:
  level: debug
```

Can be set by `GIT_SYNCER_LOGS__LEVEL` environment variable.

---

`logs.format` - logging format string, passed to python logging formatter. Default is `%(asctime)s - %(name)s - %(levelname)s - %(message)s`.

```yaml
logs:
  format: "%(message)s"
```

Can be set by `GIT_SYNCER_LOGS__FORMAT` environment variable.

#### Scheduler

`scheduler.one_time` - run only once and exit. Default is `false`.

```yaml
scheduler:
  one_time: true
```

Can be set by `GIT_SYNCER_SCHEDULER__ONE_TIME` environment variable.

---

`scheduler.executor_max_workers` - maximum number of workers to run tasks. Default is `None`.

```yaml
scheduler:
  executor_max_workers: 10
```

Can be set by `GIT_SYNCER_SCHEDULER__EXECUTOR_MAX_WORKERS` environment variable.

---

`scheduler.startup_delay` - delay before first iteration in seconds. Default is `0`.

```yaml
scheduler:
  startup_delay: 60
```

Can be set by `GIT_SYNCER_SCHEDULER__STARTUP_DELAY` environment variable.

---

`scheduler.success_delay` - delay between iterations in seconds. Default is `300`.

```yaml
scheduler:
  success_delay: 60
```

Can be set by `GIT_SYNCER_SCHEDULER__SUCCESS_DELAY` environment variable.

---

`scheduler.retry_delay` - delay between failed iterations in seconds. Default is `60`.

```yaml
scheduler:
  retry_delay: 60
```

Can be set by `GIT_SYNCER_SCHEDULER__retry_delay` environment variable.

---

`scheduler.startup_jitter` - startup delay jitter in seconds. Default is `5`.

```yaml
scheduler:
  startup_jitter: 5
```

Can be set by `GIT_SYNCER_SCHEDULER__STARTUP_JITTER` environment variable.

---

`scheduler.success_jitter` - success delay jitter in seconds. Default is `30`.

```yaml
scheduler:
  success_jitter: 30
```

Can be set by `GIT_SYNCER_SCHEDULER__SUCCESS_JITTER` environment variable.

---

`scheduler.retry_jitter` - retry delay jitter in seconds. Default is `10`.

```yaml
scheduler:
  retry_jitter: 10
```

Can be set by `GIT_SYNCER_SCHEDULER__RETRY_JITTER` environment variable.

---

`scheduler.total_timeout` - maximum time to run in seconds. Default is `0`. `0` means no timeout.

```yaml
scheduler:
  total_timeout: 600
```

Can be set by `GIT_SYNCER_SCHEDULER__TOTAL_TIMEOUT` environment variable.

---

`scheduler.close_timeout` - maximum time to wait for tasks to finish in seconds. Default is `10`.

```yaml
scheduler:
  close_timeout: 10
```

Can be set by `GIT_SYNCER_SCHEDULER__CLOSE_TIMEOUT` environment variable.

#### Repos

`repos[].source` - source repository url.

```yaml
repos:
  - source: 'https://{{env "GITHUB_USER"}}:{{secret_env "GITHUB_PASSWORD"}}@github.com/ovsds/git-syncer.git'
```

Can be enriched by environment variables.
For example:

- `{{env "GITHUB_USER"}}` will be replaced by `GITHUB_USER` environment variable.
- `{{secret_env "GITHUB_PASSWORD"}}` will be replaced by `GITHUB_PASSWORD` environment variable. Also, it will be hidden in logs.

---

`repos[].target` - target repository url.

```yaml
repos:
  - source: 'https://{{env "GITEA_USER"}}:{{secret_env "GITEA_PASSWORD"}}@gitea.ovsds.ru/ovsds/git-syncer.git'
```

Can be enriched by environment variables.

---

`repos[].include_ref` - list of refs to include. Default is `[]`.

```yaml
repos:
  - source: ...
    target: ...
    include_ref:
      - "refs/heads/main"
      - "refs/heads/develop"
```

---

`repos[].include_ref_regex` - list of regexes to include refs. Default is `[]`.

```yaml
repos:
  - source: ...
    target: ...
    include_ref_regex:
      - "refs/heads/.*"
```

If both `include_ref` and `include_ref_regex` are set, refs will be included if at least one of them matches.
If none of them are set, all refs will be included.

---

`repos[].exclude_ref` - list of refs to exclude. Default is `[]`.

```yaml
repos:
  - source: ...
    target: ...
    exclude_ref:
      - "refs/pull/.*"
```

---

`repos[].exclude_ref_regex` - list of regexes to exclude refs. Default is `[]`.

```yaml
repos:
  - source: ...
    target: ...
    exclude_ref_regex:
      - "refs/pull/.*"
```

If both `exclude_ref` and `exclude_ref_regex` are set, refs will be excluded if at least one of them matches.
If none of them are set, no refs will be excluded.
If ref is excluded, it will be deleted in target repository.
If ref in both `include` and `exclude`, it will be excluded.
