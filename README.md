# Paying out robux from a group, when the group holder has two factor authentication enabled

main.py contains example python code that does the whole process

## How it works:

### 1.
When your group payout request returns error 403 and message "Challenge is required to authorize the request", it contains two headers with data to validate your session with two factor authentication. The headers are:
   - "rblx-challenge-id": it contains the `first` challenge id used to validate the session
   - "rblx-challenge-metadata": this header contains base64 encoded table, with a `second` challenge id
### 2.
After saving both the challenge ids, you need to send a post request to the endpoint `twostepverification.roblox.com/v1/users/%group holder id%/challenges/authenticator/verify` (the response to this request will contain a verification token, used to validate your session), with body containing following json: 
```json
{
  "actionType": "Generic",
  "challengeId": "%second challenge id%",
  "code": "%your 6 digit 2fa code%"
}
```

### 3.
Now that you have the verification token, its time to validate your session. Send a post request to `apis.roblox.com/challenge/v1/continue` with body containing this json:
(Make sure to turn `challengeMetadata` value into a string. It can't be an object/dictionary.)
```json
{
  "challengeId": "%first challenge id%",
  "challengeMetadata": { "rememberDevice": false, "actionType": "Generic", "verificationToken": "%the verification token%", "challengeId": "%the second challenge id%" },
  "challengeType": "twostepverification"
}
```

### 4.
And that's it! The next payout request using the same session should successfully pay out the robux
