from flask import Flask, request, render_template
import requests
from requests.structures import CaseInsensitiveDict
import json

app = Flask(__name__)

signurl = "https://api.linkedin.com/v2/me"

upload_req_url = "https://api.linkedin.com/v2/assets?action=registerUpload"

upload_post = "https://api.linkedin.com/v2/ugcPosts"

auth_token = ""

auth_id = "urn:li:person:"


@app.route('/')
def signlog():
    return render_template('signlog.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        usert = request.form['nm']
        headers = CaseInsensitiveDict()
        headers["Accept"] = "application/json"
        headers["Authorization"] = "Bearer " + usert
        sign_res = requests.get(signurl, headers=headers)
        response_dict = json.loads(sign_res.text)
        # print(response_dict)
        if sign_res.status_code != 200:
            err = "Invalid Token"
            return render_template('signlog.html', err=err)
        else:
            global auth_id
            global auth_token
            auth_token = "Bearer " + usert
            auth_id = '"' + auth_id + response_dict["id"] + '"'
            user_name = response_dict["localizedLastName"]
            user_id = response_dict["id"]
            return render_template('file.html', user_id=user_id, user_name=user_name)


@app.route('/fileup', methods=['POST', 'GET'])
def fileup():
    if request.method == 'POST':
        url = "https://api.linkedin.com/v2/assets?action=registerUpload"
        payload = "{\r\n    \"registerUploadRequest\": {\r\n        \"recipes\": [\r\n            \"urn:li:digitalmediaRecipe:feedshare-image\"\r\n        ],\r\n        \"owner\": " + auth_id + ",\r\n        \"serviceRelationships\": [\r\n            {\r\n                \"relationshipType\": \"OWNER\",\r\n                \"identifier\": \"urn:li:userGeneratedContent\"\r\n            }\r\n        ]\r\n    }\r\n}"
        headers = {
            'Content-Type': 'text/plain',
            'Authorization': auth_token,
            'Cookie': 'lidc="b=TB26:s=T:r=T:a=T:p=T:g=4503:u=3:x=1:i=1684337340:t=1684338049:v=2:sig=AQElf-IRuw4w_ktxeSrEhKZo-RpMAtTN"; bcookie="v=2&14008946-5e6b-476c-867f-204e651b6bde"; lidc="b=TB38:s=T:r=T:a=T:p=T:g=4325:u=1:x=1:i=1684306607:t=1684393007:v=2:sig=AQELWwfJfDuoqqrv5rAqv8wmKccGz0-x"; lang=v=2&lang=en-us'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        # print(response.text)

        response_up_req = json.loads(response.text)
        # print(response)
        if response.status_code != 200:
            # print(response_up_req["message"])
            err = "error in upload request"
            return render_template('signlog.html', err=err)
        else:
            img_post_url = response_up_req["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"][
                "uploadUrl"]
            img_post_asset = response_up_req["value"]["asset"]
            # print(img_post_asset)
            file = request.files['im']
            file.save('static/result.jpg')
            upimg = open('static/result.jpg', 'rb')
            headers = {
                'Content-Type': 'image/jpeg',
                'Authorization': auth_token,
                'Cookie': 'lidc="b=TB26:s=T:r=T:a=T:p=T:g=4503:u=3:x=1:i=1684337340:t=1684338049:v=2:sig=AQElf-IRuw4w_ktxeSrEhKZo-RpMAtTN"; bcookie="v=2&14008946-5e6b-476c-867f-204e651b6bde"; lidc="b=TB38:s=T:r=T:a=T:p=T:g=4325:u=1:x=1:i=1684306607:t=1684393007:v=2:sig=AQELWwfJfDuoqqrv5rAqv8wmKccGz0-x"; lang=v=2&lang=en-us'
            }
            upload_img = requests.post(img_post_url, data=upimg, headers=headers)
            # upload_img = json.loads(upload_imgs.text)
            # print("uplade")
            # print( upload_img)
            if upload_img.status_code != 201:
                # print(upload_img["message"])
                err = "Error in upload"
                return render_template('signlog.html', err=err)
            else:
                # print(request.form["title"])
                # print(request.form["txt"])
                tit=request.form["title"]
                # print(img_post_asset)
                tx=request.form["txt"]
                newid=auth_id.replace('"', '', 2)
                post_format = {
                    "author": newid,
                    "lifecycleState": "PUBLISHED",
                    "specificContent": {
                        "com.linkedin.ugc.ShareContent": {
                            "shareCommentary": {
                                "text": '"' + request.form["txt"] + '"'
                            },
                            "shareMediaCategory": "IMAGE",
                            "media": [
                                {
                                    "status": "READY",
                                    "description": {
                                        "text": "Center stage!"
                                    },
                                    "media":  img_post_asset,
                                    "title": {
                                        "text": request.form["title"]
                                    }
                                }
                            ]
                        }
                    },
                    "visibility": {
                        "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                    }
                }
                headers = {
                    'Content-Type': 'text/plain',
                    'Authorization': auth_token,
                    'Cookie': 'lidc="b=OB26:s=O:r=O:a=O:p=O:g=4717:u=4:x=1:i=1684350792:t=1684424455:v=2:sig=AQF6v_liMBT-l74eQ6XSGqWe9LYdcXtJ"; bcookie="v=2&14008946-5e6b-476c-867f-204e651b6bde"; lidc="b=TB38:s=T:r=T:a=T:p=T:g=4325:u=1:x=1:i=1684306607:t=1684393007:v=2:sig=AQELWwfJfDuoqqrv5rAqv8wmKccGz0-x"; lang=v=2&lang=en-us'
                }
                # print(post_format)
                pf=json.dumps(post_format)
                # print(pf)

                upload_post_req = requests.request("POST", "https://api.linkedin.com/v2/ugcPosts", data=pf, headers=headers)
                # print(upload_post_req)
                # share = json.loads(upload_post_req)
                if upload_post_req.status_code != 201:
                    # print(upload_post_req["message"])
                    err = "error in post"
                    return render_template('signlog.html', err=err)
                else:
                    suc = "POSTED SUCCESSFULLY"
                    return render_template('signlog.html', suc=suc)


if __name__ == '__main__':
    app.run(debug=True)
