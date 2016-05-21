docker run --name postgresql_cyberpunkd -itd --restart always \
  --publish 5432:5432 \
  --volume /srv/docker/postgresql:/var/lib/postgresql \
  --env 'DB_USER=defaultuser' --env 'DB_PASS=defaultuserpassword' \
  --env 'PG_TRUST_LOCALNET=true' \
  --env 'DB_NAME=cyberpunkdDB' \
  sameersbn/postgresql:9.4-12
