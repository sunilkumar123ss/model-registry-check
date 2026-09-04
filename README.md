# Model registry manifest check

Validate version uniqueness, local artifact SHA-256 integrity, stage values, one production version per model, and evaluation metadata for production entries.

~~~sh
python3 main.py --input example.json --artifact-root .
python3 -m unittest -v
~~~

Artifacts must resolve inside the supplied root; absolute paths, parent escapes, and symlink escapes are rejected. Versions use a simple three-part numeric format without prerelease/build suffixes. Production records require a dataset identifier and finite numeric metrics.

The supplied artifact is a synthetic configuration file, not trained weights. Its production stage is only a manifest-validation scenario and does not indicate a deployed model. Checksums detect changed bytes, not trusted authorship. This demo has no signatures, access controls, remote registry, quality policy, promotion workflow, or race-free artifact serving.

## Scope

This is an educational implementation with synthetic fixtures. Run the tests and inspect the documented limits before adapting it.

## Repository checks

```sh
python3 verify.py
```

This runs the isolated test suite, synthetic example, and CLI help. The included GitHub Actions workflow repeats these checks when the repository is published. No hosted CI result is claimed by the local verification report.
