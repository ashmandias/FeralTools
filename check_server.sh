#!/bin/bash

#HOST=zeus.feralhosting.com

HOSTNAME="${1}"

DETAILS="${2}"

# to lower
HOSTNAME=$(echo "${HOSTNAME}" | tr A-Z a-z)
# remove .FERALHOSTING.COM
HOSTNAME="$(echo ${HOSTNAME} | sed 's|.feralhosting.com||g')"
# remove non-letters
#HOSTNAME="$(echo ${HOSTNAME} | sed 's/[^a-zA-Z]//g')"
HOSTNAME=${HOSTNAME//[^a-z]/}

HOST="${HOSTNAME}.feralhosting.com"

IP_PREFIX="185"
HOST_IP="$(nslookup "${HOST}" | grep "${IP_PREFIX}" | awk '{print $2}')"
BAD_IP="$(nslookup fake.feralhosting.com | grep "${IP_PREFIX}" | awk '{print $2}')"

if [[ "${BAD_IP}" == "${HOST_IP}" ]]; then
	echo -n "no such host"
	exit
fi

#SLEEP="2"
PING_COUNT="10"
TIMEOUT="5s"

FTP_SERVER="ProFTPD"
SSH_SERVER="OpenSSH"

COLOR_GOOD="\x0303"
COLOR_WARN="\x0307"
COLOR_BAD="\x0305"
COLOR_END="\x03"

colorize(){
	SERVICE="${1}"
	STATUS="${2}"
	if [[ "${STATUS}" == "Up" ]]; then
		echo "${COLOR_GOOD}${SERVICE}: ${STATUS}${COLOR_END}"
	elif [[ "${STATUS}" =~ 0%.* ]]; then
		echo "${COLOR_GOOD}${SERVICE}: ${STATUS}${COLOR_END}"
	elif [[ "${STATUS}" == "Down" ]]; then
		echo "${COLOR_BAD}${SERVICE}: ${STATUS}${COLOR_END}"
	elif [[ "${STATUS}" =~ 100%.* ]]; then
		echo "${COLOR_BAD}${SERVICE}: ${STATUS}${COLOR_END}"
	else
		echo "${COLOR_WARN}${SERVICE}: ${STATUS}${COLOR_END}"
	fi
}

format_service_string(){
	SERVICE="${1}"
	STATUS="${2}"
	DESCRIPTION="${3}"

	if [[ "${DETAILS}" == "true" ]]; then
		colorize "${SERVICE} ${DESCRIPTION}" "${STATUS}"
	else
		colorize "${SERVICE}" "${STATUS}"
	fi
}


FTP="$(echo "quit" | timeout "${TIMEOUT}" nc "${HOST}" 21 2> /dev/null | grep -c "${FTP_SERVER}")" 2> /dev/null

if [[ "${FTP}" -eq 1 ]]; then
	FTP_RETURN="Up"
else
	FTP_RETURN="Down"
fi

FTP_STATUS="$(format_service_string "FTP" "${FTP_RETURN}" "(banner checked on port 21)")"

SSH="$( echo "quit" | timeout "${TIMEOUT}" nc "${HOST}" 22 2> /dev/null | grep -c "${SSH_SERVER}")" 2> /dev/null

if [[ "${SSH}" -eq 1 ]]; then
	SSH_RETURN="Up"
else
	SSH_RETURN="Down"
fi

SSH_STATUS="$(format_service_string "SSH" "${SSH_RETURN}" "(banner checked on port 22)")"

HTTP=$(timeout ${TIMEOUT} curl "${HOST}" -s > /dev/null; echo $?)
if [[ "${HTTP}" -eq 0 ]]; then
	HTTP_RETURN="Up"
else
	HTTP_RETURN="Down"
fi

HTTP_STATUS="$(format_service_string "HTTP" "${HTTP_RETURN}" "(Server-wide, not per-user)")"

PING="$(timeout "${TIMEOUT}" ping -A -q -c "${PING_COUNT}" "${HOST}" | grep transmitted)"

if [[ "${PING}x" == "x" ]]; then
	PING="100"
fi

[[ "${PING}" =~ [0-9]+% ]]

PING_PERCENT="${BASH_REMATCH}"

PING_STATUS="$(format_service_string "Ping" "${BASH_REMATCH} loss" "(Based on ${PING_COUNT} Pings)")"

if [[ "${DETAILS}" == "true" ]]; then
	REPLY="${HOSTNAME^} status: ${PING_STATUS} | ${FTP_STATUS} | ${SSH_STATUS} | ${HTTP_STATUS} | Checks preformed from a ${COLOR_GOOD}non-Feral${COLOR_END} host located in ${COLOR_BAD}Canada${COLOR_END}."
else
	REPLY="${HOSTNAME^} status: ${PING_STATUS} | ${FTP_STATUS} | ${SSH_STATUS} | ${HTTP_STATUS} |"
fi

echo "$(date): ${REPLY}" >> ${HOME}/out/status-$(date -I).log
echo -ne "${REPLY}"
