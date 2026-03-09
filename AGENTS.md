# AGENTS

## Commit Messages

All agents working in this repository must use Conventional Commits for every
commit they create.

Use this format:

```text
type(scope): summary
```

Examples:

```text
feat(auth): add support for audience validation
fix(config): reject invalid denylist settings
docs(release): document bootstrap tag setup
chore(ci): consolidate release workflow
```

Rules:

- Use `feat` for user-visible features. This triggers a minor release.
- Use `fix` and `perf` for patch-level changes. These trigger a patch release.
- Mark breaking changes with `!` in the header or a `BREAKING CHANGE:` footer.
- Keep the summary short and imperative.
- Do not use free-form commit messages, because release automation depends on
  Conventional Commits to calculate the next semantic version and generate the
  changelog.
