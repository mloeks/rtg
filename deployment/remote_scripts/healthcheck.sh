#!/usr/bin/env bash
# TODO set back to admin@royale-tippgemeinschaft.de once account works again ... :-(
# TODO remove --insecure curl flag once auto renewed certificates are properly understood by curl on the server again
# (this broke after the automatic cert renewal which otherwise seemed to work normally on 11/12/2020)
HEALTH_STATUS=$(curl --insecure -s -o /dev/null -w "%{http_code}" 'https://api.royale-tippgemeinschaft.de/healthcheck/')
if [[ $HEALTH_STATUS != 200 ]]; then
    mail -s "[RTG] PROD - Service unhealthy ($HEALTH_STATUS)" matthias@loeks.net <<<\
        "RTG Backend service is currently unavailable. Health endpoint returned status code $HEALTH_STATUS."
else
    echo "Health OK."
fi