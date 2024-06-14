# Git Syncer

Git Syncer is easy-to-use git repository mirror tool.
Mirroring will create/update/delete refs in the target repository to match the source repository.
WARNING: Never use repository with working data as target repository, it will be overwritten.

## Usage

It can be run in docker, example:

```shell
docker run \
  --rm \
  --volume ./backend/examples/settings.yaml:/settings.yaml \
  --env GIT_SYNCER_SETTINGS_YAML=/settings.yaml \
  --env GITHUB_USER \
  --env GITHUB_PASSWORD \
  --env GITEA_USER \
  --env GITEA_PASSWORD \
  ghcr.io/ovsds/git-syncer:0.1.0
```

with `examples/settings.yaml`:

```yaml
scheduler:
  one_time: true
repos:
  - source: 'https://{{env "GITHUB_USER"}}:{{secret_env "GITHUB_PASSWORD"}}@github.com/ovsds/git-syncer.git'
    target: 'https://{{env "GITEA_USER"}}:{{secret_env "GITEA_PASSWORD"}}@gitea.ovsds.ru/ovsds/git-syncer.git'
    exclude_ref_regex:
      - "refs/pull/.*"
```

more information can be found in [backend/README.md](backend/README.md#Settings).

## Development

### Global dependencies

- node

### Taskfile commands

For all commands see [Taskfile](Taskfile.yaml) or `task --list-all`.

## License

[MIT](LICENSE)
