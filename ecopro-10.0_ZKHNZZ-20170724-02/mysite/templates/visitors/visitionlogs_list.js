{% autoescape off %}
[
{% for item in latest_item_list %}
{
"id":"{{item.id}}",
"VisempName":"{% if can_change %}{% ifequal item.VisState 0 %}<a class='can_edit'  href='#' onclick='javascript:editclick({{item.id}});'>{{item.VisempName|default:"" }}</a>{% else %}{{item.VisempName|default:"" }}{% endifequal %}{% else %}{{item.VisempName|default:"" }}{%endif%}",
"VisGender":"{{item.get_VisGender_display|default:""}}",
"CertificateType":"{{item.get_CertificateType_display|default:"" }}",
"SSN":"{{item.SSN|default:"" }}",
"EnterTime":"{{item.EnterTime|default:"" }}",
"ExitTime":"{{item.ExitTime|default:"" }}",
"VisitingNum":"{{item.VisitingNum|default:"" }}",
"VisitedCompany":"{{ item.VisitedCompany|default:"" }}",
"InterviewedempName":"{{item.InterviewedempName|default:"" }}",
"EnterArticles":"{{item.EnterArticles|default:"" }}",
"ExitArticles":"{{item.ExitArticles|default:"" }}",
"Tele":"{{item.Tele|default:"" }}",
"National":"{{item.National|default:"" }}",
"Birthday":"{{item.Birthday|default:"" }}",
"Address":"{{item.Address|default:"" }}",
"LicenseOrg":"{{item.LicenseOrg|default:"" }}",
"VisCompany":"{{item.VisCompany|default:"" }}",
"VisReason":"{{item.VisReason|default:"" }}",
"VisState":"{{item.get_VisState_display|default:"" }}",
"photo":"{{ item|thumbnailUrl }}",
"photoz":"{{ item|thumbnailUrlz }}"
}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
