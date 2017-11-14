#!/bin/bash
##BACKUP the database
FOLDER=/djangoProject/tmp/db_backups
now="$(date +'%d-%m-%Y')"
SQLFILE=$FOLDER/$now.sql.txt
sudo -u postgres pg_dump -F p clims_db > $SQLFILE
##cp to amazon here
/home/ubuntu/.local/bin/aws s3 cp $SQLFILE  s3://dekkerlab-web/db-backups/ &> /home/ubuntu/aws_backup_result.txt
#rm the file
rm $SQLFILE
#BACKUP the media files
/home/ubuntu/.local/bin/aws s3 sync /djangoProject/cLIMS/media s3://dekkerlab-web/media-backups
