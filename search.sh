#!/bin/bash
set -ueo pipefail

kind=${1:-}
term=${2:-}
provider=${3:-premiumize}
max_results=5

if [ -z "${kind}" ] || [ -z "${term}" ]; then
	echo "Usage: $0 <kind> <term> [provider]"
	exit 1
fi

if [ "${provider}" == "real_debrid" ]; then
	debrid_api_key=$(op read "op://Personal/Real-debrid/API Token")
elif [ "${provider}" == "premiumize" ]; then
	debrid_api_key=$(op read "op://Personal/Premiumize.me/API Key")
else
	echo "Invalid provider: ${provider}"
	exit 1
fi

config=$(cat <<-EOF | jq -c . | base64 -w0
{
	"debrid_service": "${provider}",
	"debrid_api_key": "${debrid_api_key}",
	"max_results": ${max_results},
	"indexers": ["yts", "eztv", "kickasstorrents-ws", "thepiratebay", "therarbg", "torrentgalaxy"]
}

EOF
)

echo "${term}" \
	| tr ',' '\n' \
	| xargs -I{} -P17 \
		http --timeout 60 \
			GET \
			"http://127.0.0.1:8000/${config}/stream/${kind}/{}.json"
