import requests
import base64
import json
import pyotp # this import is just for generating the 2fa code

# put your account token (roblosecurity) here
account_token=""

# put your group id here
group_id=0

# put user id of the player you want to send robux to here
user_id=0

# put the amount of robux to send here
robux_amount=0

# two factor secret to generate the 6 digit 2fa code
twofactor_secret=""





# actual code below


# generate the 2fa code
totp = pyotp.TOTP(twofactor_secret)
twofactorcode = totp.now()
# end of generating the 2fa code


# variables for the whole process
full_cookie=".ROBLOSECURITY="+account_token
csrf_token = requests.post("https://auth.roblox.com/v2/logout", headers={'Cookie':full_cookie}).headers['X-CSRF-TOKEN'] # gets the csrf token
payout_request_body = {
    "PayoutType": "FixedAmount",
    "Recipients": [
        {
            "amount": robux_amount,
            "recipientId": user_id,
            "recipientType": "User"
        }
    ]
}

# function to request the payout
def request_payout():
    payout_request = requests.post("https://groups.roblox.com/v1/groups/" + str(group_id) + "/payouts", headers={'Cookie': full_cookie, 'X-CSRF-TOKEN': csrf_token}, json=payout_request_body)
    if (payout_request.status_code == 403 and payout_request.json()["errors"][0]["message"] == "Challenge is required to authorize the request"):
        return payout_request
    elif (payout_request.status_code == 200):
        print("Robux successfully sent!")
        return False
    else:
        print("payout error")
        print(payout_request.json()["errors"][0]["message"])
        return False

data = request_payout()
if (data == False):
    exit()

# get necessary data for the 2fa validation
challengeId = data.headers["rblx-challenge-id"]
metadata = json.loads(base64.b64decode(data.headers["rblx-challenge-metadata"]))
metadata_challengeId = metadata["challengeId"]
senderId = metadata["userId"]


# make the actual 2fa validation
twofactor_request_body = {
    "actionType": "Generic",
    "challengeId": metadata_challengeId,
    "code": twofactorcode
}
twofactor_request = requests.post("https://twostepverification.roblox.com/v1/users/"+senderId+"/challenges/authenticator/verify", headers={'Cookie': full_cookie, 'X-CSRF-TOKEN': csrf_token}, json=twofactor_request_body)

if ("errors" in twofactor_request.json()):
    print("2fa error")
    print(twofactor_request.json()["errors"][0]["message"])
    exit()

# the 2fa code worked!
verification_token = twofactor_request.json()["verificationToken"]

# now it's time for the continue request (it's really important)
continue_request_body = {
    "challengeId": challengeId,
    "challengeMetadata": json.dumps({
        "rememberDevice": False,
        "actionType": "Generic",
        "verificationToken": verification_token,
        "challengeId": metadata_challengeId
    }),
    "challengeType": "twostepverification"
}
continue_request = requests.post("https://apis.roblox.com/challenge/v1/continue", headers={'Cookie': full_cookie, 'X-CSRF-TOKEN': csrf_token}, json=continue_request_body)

# everything should be validated! making the final payout request.
print("Went through 2fa stuff!")
data = request_payout()
if (data == False):
    exit()
print("If you see this message, the 2fa validation didn't work.")