#!/usr/bin/env bash
# TODO set back to admin@royale-tippgemeinschaft.de once account works again ... :-(
HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" 'https://api.royale-tippgemeinschaft.de/healthcheck/')
if [[ $HEALTH_STATUS != 200 ]]; then
    mail -s "[RTG] PROD - Service unhealthy ($HEALTH_STATUS)" matthias@loeks.net <<<\
        "RTG Backend service is currently unavailable. Health endpoint returned status code $HEALTH_STATUS."
else
    echo "Health OK."
fi