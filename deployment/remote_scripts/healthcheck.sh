#!/usr/bin/env bash
HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" 'https://api.royale-tippgemeinschaft.de/healthcheck/')
if [[ $HEALTH_STATUS != 200 ]]; then
    mail -s "[RTG] PROD - Service unhealthy ($HEALTH_STATUS)" admin@royale-tippgemeinschaft.de <<<\
        "RTG Backend service is currently unavailable. Health endpoint returned status code $HEALTH_STATUS."
else
    echo "Health OK."
fi