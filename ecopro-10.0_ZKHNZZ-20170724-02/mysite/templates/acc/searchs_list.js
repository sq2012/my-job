{% autoescape off %}
{% load i18n %}
[
{% for item in latest_item_list %}
{
"id":"{{ item.id }}",
"SN":"{{ item.SN }}",
"Alias":"{{ item.Alias|default:'' }}",
"Protype":"{{ item.Protype|default:'' }}",
"MAC":"{{ item.MAC }}",
"State":"{{ item.getDynState|getStateStr }}",
"IPAddress":"{{ item.IPAddress|default:'' }}",
"NetMask":"{{ item.NetMask|default:'' }}",
"GATEIPAddress":"{{ item.GATEIPAddress|default:'' }}",
"FWVersion":"{{ item.FWVersion|default:'' }}",
"OP":"<a href='#' style='color:green;text-decoration: underline;'onclick='edit_searchs({{item.id}});'>编辑</a>&nbsp;&nbsp;<a href='#' style='color:green;text-decoration: underline;'onclick='save_searchs({{item.id}});'>保存并修改设备</a>",

"WebServerIP":"{{ item.WebServerIP|default:'' }}",
"WebServerURL":"{{ item.WebServerURL|default:'' }}",
"WebServerPort":"{{ item.WebServerPort|default:'' }}",
"IsSupportSSL":"{{ item.IsSupportSSL|default:'' }}",
"DNSFunOn":"{{ item.DNSFunOn|isYesNo }}",
"DNS":"{{ item.DNS|default:'' }}",
"Reserved":"{{ item.Reserved|default:'' }}",
"DeviceName":"{{ item.DeviceName }}",
"isAdd":"{{ item|isAddIclock }}"
}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
