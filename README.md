# SentinelOne-API
Some Python SentinelOne API request examples and UI

Python Version 2.7
SentinelOne API version 1.6

This is a collection of API requests for SentinelOne that can be built upon further.  The easiest way I've found to navigate systems is by utilizing the internal ip to look up agentIDs which then can be passed through various different functions from the API.  I'm unsure if the Agent Actions or Machine API requests are functional from sentinelOne but we can get by without utilizing them There is also the "passphrase" which can beeasily obtained through the API but does not seem to be important for uninstallingagents through the API.The most difficult aspect is the inconsistent and wildly constructed json responses and learning how to parse through the information to find what you need


will need to change all request url's to be specific to your account
