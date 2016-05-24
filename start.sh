service docker restart
docker run -p 9000:9000 -p 8000:8000 -v /srv/buildingdepot/Documentation/build/html/:/var/www/html -t -i bamos/openface /bin/bash