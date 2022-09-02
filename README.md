# availability-watchers

## Setup

1. Create gmail API client credentials on the gCloud console and save them to client_secret.json.
1. The first time you run the script, it will redirect to a Google oAuth login page. Log in with the account you want to send the notification emails.

## Usage

Create your own `config.yaml` based on the example.

Run every 5 minutes with:

```
*/5 * * * * /home/popcornisgood/code/availability-watchers/cron_script.sh config.yaml >> /home/popcornisgood/code/availability-watchers/log 2>&1
```
