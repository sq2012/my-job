{% autoescape off %}
{% load iclock_tags %}

[
{% for item in latest_item_list %}
{"id":"{{ item.SN }}",
"SN":"{% if can_change %}<a class='can_edit'  href='#' onclick='javascript:editclick(\"{{item.SN}}\");'>{{ item.SN }}</a>{% else %}{{ item.SN }}{% endif %}",
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
"DeptIDS":"<a title='归属明细' onclick='getdpts_iclock(\"{{ item.SN }}\")' style='color:green;'>{{ item|deptShowStr }}</a>",
"Data_":"&nbsp;<a  title='服务器下发命令日志' onclick='getLog_device(\"{{ item.SN }}\")'style='color:green;'>C</a>&nbsp;<a title='原始记录'style='color:green;' onclick='getTran(\"{{ item.SN }}\")'>L</a>&nbsp;<a title='设备上传数据日志' style='color:green;' onclick='getUplog(\"{{ item.SN }}\")'>U</a>&nbsp;<a  title='设备上的人员名单' style='color:green;' onclick='getempofdevice_iclock(\"{{ item.SN }}\")'>E</a>&nbsp;{% if user|HasPerm:"iclock.browselogPic" %}<a  title='记录照片'  style='color:green;' onclick='getpitureofdevice(\"{{ item.SN }}\")'>P</a>{% endif %}",
"Data_pos":"&nbsp;<a  title='服务器下发命令日志' onclick='getLog_device(\"{{ item.SN }}\")'style='color:green;'>C</a>&nbsp;<a title='消费明细'style='color:green;' onclick='getPosTran(\"{{ item.SN }}\")'>L</a>&nbsp;",
"Data_acc":"&nbsp;<a  title='服务器下发命令日志' onclick='getLog_device(\"{{ item.SN }}\")'style='color:green;'>C</a>&nbsp;<a title='门禁记录'style='color:green;' onclick='getAccTran(\"{{ item.SN }}\")'>L</a>&nbsp;<a title='设备上传数据日志' style='color:green;' onclick='getUplog(\"{{ item.SN }}\")'>U</a>&nbsp;<a  title='设备上的人员名单' style='color:green;' onclick='getempofdevice_iclock(\"{{ item.SN }}\")'>E</a>",
"Authentication":"{{ item.get_Authentication_display }}",
"AlgVer":"{{ item.GetDevice.AlgVer|default:'' }}",
"pushver":"{{ item.GetDevice.pushver }}",
"CommType":"{{ item.GetCommType|default:''  }}",
"Memo":"{{ item.GetDevice|device_memo }}",
"getImgUrl":"{{ item.getImgUrl }}"}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
