##This is the Readme of Clims.

##Run following commands for the cLIMS setup

git clone https://github.com/dekkerlab/cLIMS-docker.git

cd cLIMS-docker/Docker/

docker-compose -f production_docker-compose.yml build

chmod 755 initialize.sh

##Initialize with your s3 backup dump <YYYY/MM/DD>

./initialize.sh 2017/11/14

docker-compose -f production_docker-compose.yml up -d
  
