{% autoescape off %}
{% load iclock_tags %}

[
{% for item in latest_item_list %}
{"id":"{{ item.SN }}",
"SN":"{{item.SN}}",
"Alias":"{{ item.Alias|default:'' }}",
"Dept":"{{ item.BackupDev|default:'' }}",
"IPAddress":"{{ item.GetDevice.IPAddress|default:'' }}",
"State":"{{ item.getDynState|getStateStr }}",
"LastActivity":"{{ item.GetDevice.LastActivity|shortDTime|default:'' }}",
"PosLogStamp":"{{ item.GetDevice|show_LastLogStamp }}",
"LastLogId":"{{ item.GetDevice|show_LastLogId|default:'' }}",
"LogStamp":"{{ item.GetDevice.LogStamp|transLogStamp|default:"" }}",
"FWVersion":"{{ item.GetDevice.FWVersion|default:'' }}",
"City":"{{ item.City|default:'' }}",
"DeviceName":"{{ item.DeviceName|default:'' }}",
"UserCount":"{{ item.GetDevice.UserCount|default:'' }}",
"FPCount":"{{ item.GetDevice.FPCount|default:'' }}",
"FaceCount":"{{ item.GetDevice.faceNumber|default:'' }}",
"TransactionCount":"{{ item.GetDevice.TransactionCount|default:'' }}",
"MaxAttLogCount":"{{ item.GetDevice.MaxAttLogCount|default:'120000' }}",
"MaxUserCount":"{{ item.GetDevice.MaxUserCount|default:'' }}",
"ProductType":"{{ item.GetDevice.ProductType|show_ProductType }}",
"DeptIDS":"{{ item|deptShowStr }}",
"AlgVer":"{{ item.GetDevice.AlgVer|default:'' }}",
"pushver":"{{ item.GetDevice.pushver }}",
"CommType":"{{ item.GetCommType }}",
"Memo":"{{ item|device_memo }}"}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
