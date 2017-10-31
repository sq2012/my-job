{% autoescape off %}
[
{% for item in latest_item_list %}
{"id":"{{ item.id }}",
"reasonNo":"{% if can_change %}<a class='can_edit'  href='#' onclick='javascript:editclick({{item.id}});'>{{ item.reasonNo|default:"" }}</a>{% else %}{{ item.reasonNo|default:"" }}{% endif %}",
"reasonName":"{{ item.reasonName }}"
}{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
