# Twitter Stats

## How to run from VSCode

1. Open PS Terminal.
1. Make sure it runs `.venv/Scripts/Activate.ps1`.
1. Set environment variable `TOKEN` to your bearer token from Twitter Developer Portal, using this command:
`$env:TOKEN = "<your_token>"`.
1. Set environment variable `CONNECTION_STRING` for accessing Storage Account.
1. Make sure Azurite is installed, and run Azurite Blob Service (`Azurite: Start` from Command Palette). It should be listening on port 10000.
1. Run `func start`.

## Remaining work
* Pass bearer token to code in production (KeyVault?)
* Same for connection strings to Queues/Tables
* Add more stats such as:
  * Total number of tweets
  * Total number of likes/retweets/quotes/comments
  * Tweet to like ratio
  * `liked_tweets` metric
* Edge cases:
  * 429 while handling a user
  * User responding twice
  * Non-429 error during processing
  * ...
