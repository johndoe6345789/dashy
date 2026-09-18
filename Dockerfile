# Dashy with this repo's config baked in. CapRover builds this via
# captain-definition; pin the tag so a Dashy release can't change the
# dashboard (or its config schema) under us unannounced.
FROM lissy93/dashy:4.7.3
COPY conf.yml apps.yml /app/user-data/
