#!/bin/sh
uwsgi --ini /usr/local/src/tethys/uwsgi_deploy.ini &
celery beat -l info -f /tmp/celery_beat.log $@ &
exec celery worker -l info -f /tmp/celery_worker.log $@
