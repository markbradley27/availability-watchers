# availability-watchers

## Setup

1. Populate `.env` file with Mailjet API keys.
1. `mkdir availability_files`

## Usage

Create your own `config.yaml` based on the example.

Run every 5 minutes with:

```
*/5 * * * * /home/popcornisgood/code/availability-watchers/cron_script.sh config.yaml >> /home/popcornisgood/code/availability-watchers/log 2>&1
```
