# UXPluginVersions

The latest version of each plugin, one file per plugin, read by plugin releases that predate uxmCore. Newer releases ask uxplima.com directly.

The files are written by the `sync` workflow every hour from the store's latest release. Never edit them by hand: the next run would overwrite the change. The table of file names and product numbers is in `.github/sync_versions.py`.

Old plugin jars keep reading these files for as long as servers run them, so this repository must not be deleted or made private.

GitHub pauses scheduled workflows in a repository that has had no commit for 60 days. If the files stop following the store, enable `sync` again on the Actions tab or run it by hand there.
