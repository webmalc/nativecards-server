{% for part_of_speach, values in entries.items %}
[{{ part_of_speach }}] {% for value in values %}{{ value }}{% if not forloop.last %}, {% endif %}{% endfor %}
{% endfor %}
