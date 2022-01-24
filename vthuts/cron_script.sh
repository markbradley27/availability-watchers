set -x
source ../venv/bin/activate
python3 vthutwatcher.py --notify_email $1 --notifier_email $2 --notifier_password $3
deactivate
