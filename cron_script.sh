set -x
cd "$(dirname "$0")"
. ./venv/bin/activate
python3 main.py --config_file $1
