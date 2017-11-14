#!/bin/bash
##BACKUP the database
FOLDER="/home/ubuntu/db_backups"
now_local=`date +'%Y-%m-%d'`
now_s3=`date +'%Y/%m/%d'`
SQLFILE=$FOLDER/${now_local}.sql.txt
docker exec -u postgres docker_db_1 pg_dump -F p clims_db > $SQLFILE
##cp to amazon here
/usr/local/bin/aws s3 cp $SQLFILE  s3://dekkerlab-web/db-backups/${now_s3}.sql.txt &> /home/ubuntu/aws_backup_result.txt
#rm the file
rm $SQLFILE
#BACKUP the media files
/usr/local/bin/aws s3 sync /home/ubuntu/media s3://dekkerlab-web/media-backups
