import top.api


appkey = "23642933"
appsecret = "e3539164ac2bcb43d3a34654a4a5e5e7"
req = top.api.AlibabaAliqinFcSmsNumSendRequest("https://gw.api.tbsandbox.com/router/rest", 80)
req.set_app_info(top.appinfo(appkey, appsecret))

req.sms_type="normal"
req.sms_free_sign_name=""
req.sms_param="{\"website\":\"赶集网\"}"
req.rec_num="15527811219"
req.sms_template_code="SMS_48035143"
try:

    f = req.getResponse()
    print(f)
except Exception as e:
    print(e)