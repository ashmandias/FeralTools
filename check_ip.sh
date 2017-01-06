#!/bin/bash

#HOST=zeus.feralhosting.com

HOSTNAME="${1}"

# to lower
HOSTNAME=$(echo "${HOSTNAME}" | tr A-Z a-z)
# remove .FERALHOSTING.COM
HOSTNAME="$(echo ${HOSTNAME} | sed 's|.feralhosting.com||g')"
# remove non-letters
#HOSTNAME="$(echo ${HOSTNAME} | sed 's/[^a-zA-Z]//g')"
HOSTNAME=${HOSTNAME//[^a-z]/}


HOST="${HOSTNAME}.feralhosting.com"
#HOST="google.com"

IP_PREFIX="185"
#HOST_IP="$(nslookup "${HOST}" | grep "${IP_PREFIX}" | awk '{print $2}')"
HOST_IP="$(host "${HOST}" | grep "has address" | awk '{print $4}')"
HOST_IPv6="$(host "${HOST}" | grep "has IPv6 address" | awk '{print $5}')"
#BAD_IP="$(nslookup fake.feralhosting.com | grep "${IP_PREFIX}" | awk '{print $2}')"
BAD_IP="$(host "fake.feralhosting.com" | grep "has address" | awk '{print $4}')"

if [[ "${BAD_IP}" == "${HOST_IP}" ]]; then
	echo -n "The host "${HOST} does not appear to exist""
	exit
else
	echo -n "The IP for ${HOST} is ${HOST_IP}"
fi

if [[ "${HOST_IPv6}x" != "x" ]]; then
	echo -n "; The IPv6 address is ${HOST_IPv6}"
fi




