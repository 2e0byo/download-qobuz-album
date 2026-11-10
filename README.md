# A small script to download a purchased Qobuz album

Recently I had to download a qobuz album I had purchased which was apparently
too large to download as a single zip.  Here is a script to extract the track
download links from a saved page, send them to the server to get the download
links, and then write out a script calling `curl` to do the final download.

`COOKIE` (the env var) should contain the logged-in session cookie, as sent with
an request to the server (use devtools).  We request format `6`, which at time of
writing is `.flac`.
