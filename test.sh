#!/bin/bash
colorize(){
	SERVICE="${1}"
	STATUS="${2}"
	echo "$SERVICE STATUS"
}

echo "$(colorize ftp up)"
