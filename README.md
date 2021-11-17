# dockersolarrs485mqtt

sudo apt install gnupg2 pass
docker image build -t solarrs485mqtt:latest  .
docker login -u revenberg
docker image push revenberg/solarrs485mqtt:latest

docker run revenberg/solarrs485mqtt


docker exec -it ??? /bin/sh

docker push revenberg/solarrs485mqtt:latest

# /home/pi/dockersolarrs485mqtt/build.sh;docker rm -f $(docker ps | grep solarrs485mqtt | cut -d' ' -f1);cd /var/docker-compose;docker-compose up -d solarrs485mqtt;docker logs -f $(docker ps | grep solarrs485mqtt | cut -d' ' -f1)
