# Instabackup

Backup Instapaper locally, with (relatively) smart incremental backups.

Get an OAuth client ID/secret from [here](https://www.instapaper.com/main/request_oauth_consumer_token). Then, 

```
$ pip3 install git+https://github.com/danmarg/Instabackup.git
$ instabackup --username <your username> --password <your password> --client_id <your client ID> --client_secret <your client secret> --backup <backup dir>
```
