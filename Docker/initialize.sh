#!/bin/bash

###############
# USAGE
# script.sh <db-snapshot-date:YYYY/MM/DD> <LOCAL:optional>
# It creates the required folders for docker containers
#
# If the second argument is given then runs in local mode and does not
# grab backups from S3. If $2 is NOT given, then,
# It grabs the database snap shto from s3 baed on the given date
# given in YYYY/MM/DD and copied the media files in aws s3 to the media folder


POSTGRESFOLDER="../../pgdata"
STATICFOLDER="../../static"
DBINITFOLDER="../../db_backups"

MEDIAFOLDER="../../media"

##################################################

if [ ! -d $POSTGRESFOLDER ];
then
   mkdir $POSTGRESFOLDER
fi

if [ ! -d $STATICFOLDER ];
then
   mkdir $STATICFOLDER
fi

if [ ! -d $DBINITFOLDER ];
then
    mkdir $DBINITFOLDER
fi

###################################################

#COMPOSEFILE=development_docker-compose.yml

DBFILE=$1.new.sql.txt

if [ ! $2 ];
then
  aws s3 cp s3://dekkerlab-web/db-backups/$DBFILE $DBINITFOLDER/initial.sql.txt
  aws s3 cp --recursive s3://dekkerlab-web/media-backups $MEDIAFOLDER
fi

chmod 755 scripts/backup_to_s3.sh
