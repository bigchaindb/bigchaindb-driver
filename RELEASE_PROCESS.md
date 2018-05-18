# Our Release Process

## Notes

BigchainDB follows
[the Python form of Semantic Versioning](https://packaging.python.org/tutorials/distributing-packages/#choosing-a-versioning-scheme)
(i.e. MAJOR.MINOR.PATCH),
which is almost identical
to [regular semantic versioning](http://semver.org/), but there's no hyphen, e.g.

- `0.9.0` for a typical final release
- `4.5.2a1` not `4.5.2-a1` for the first Alpha release
- `3.4.5rc2` not `3.4.5-rc2` for Release Candidate 2

**Note 1:** For Git tags (which are used to identify releases on GitHub), we append a `v` in front. For example, the Git tag for version `2.0.0a1` was `v2.0.0a1`.

We use `0.9` and `0.9.0` as example version and short-version values below. You should replace those with the correct values for your new version.

We follow [BEP-1](https://github.com/bigchaindb/BEPs/tree/master/1), which is our variant of C4, the Collective Code Construction Contract, so a release is just a [tagged commit](https://git-scm.com/book/en/v2/Git-Basics-Tagging) on the `master` branch, i.e. a label for a particular Git commit.

The following steps are what we do to release a new version of _BigchainDB Python Driver_.

## Steps

1. Create a pull request where you make the following changes:

   - Update `CHANGELOG.md`
   - In `bigchaindb-driver/__init__.py`:
     - update `__version__` to e.g. `0.9.0` (with no `.dev` on the end)
   - In `setup.py` update the version and _maybe_ update the development status item in the `classifiers` list. For example, one allowed value is `"Development Status :: 5 - Production/Stable"`. The [allowed values are listed at pypi.python.org](https://pypi.python.org/pypi?%3Aaction=list_classifiers).
   - In `README.rst` update the `Compatibility Matrix`

1. **Wait for all the tests to pass!**
1. Merge the pull request into the `master` branch.
1. Go to the [bigchaindb/bigchaindb-driver Releases page on GitHub](https://github.com/bigchaindb/bigchaindb-driver/releases)
   and click the "Draft a new release" button.
1. Fill in the details:
   - **Tag version:** version number preceded by `v`, e.g. `v0.9.1`
   - **Target:** the last commit that was just merged. In other words, that commit will get a Git tag with the value given for tag version above.
   - **Title:** Same as tag version above, e.g `v0.9.1`
   - **Description:** The body of the changelog entry (Added, Changed, etc.)
1. Click "Publish release" to publish the release on GitHub.
1. On your local computer, make sure you're on the `master` branch and that it's up-to-date with the `master` branch in the bigchaindb/bigchaindb-driver repository (e.g. `git fetch upstream` and `git merge upstream/master`). We're going to use that to push a new `bigchaindb-driver` package to PyPI.
1. Make sure you have a `~/.pypirc` file containing credentials for PyPI or just enter them manually.
1. Do `make release` to build and publish the new `bigchaindb-driver` package on PyPI.
    For this step you need to have `twine` installed
1. [Log in to readthedocs.org](https://readthedocs.org/accounts/login/) and go to the **BigchainDB Python Driver** project, then:
   - Go to Admin --> Advanced Settings
     and make sure that "Default branch:" (i.e. what "latest" points to)
     is set to the new release's tag, e.g. `v0.9.1`.
     (Don't miss the `v` in front.)
   - Go to Admin --> Versions
     and under **Choose Active Versions**, do these things:
     1. Make sure that the new version's tag is "Active" and "Public"
     1. Make sure the **stable** branch is _not_ active.
     1. Scroll to the bottom of the page and click the "Submit" button.

Congratulations, you have released a new version of BigchainDB Python Driver!

## Post-Release Steps
Update the BigchainDB Python Driver version in the `acceptance/python/Dockerfile` in the [BigchainDB Server](https://github.com/bigchaindb/bigchaindb).


