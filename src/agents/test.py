import re
import json


answer = """```json
{
 "type": "sql",
 "query": "SELECT user_id FROM transactions WHERE username = 'FZwdkpHZ'"
}
```"""
json_str = re.sub(r'`|python|json|java', '', answer).strip()
print(json_str)
answer_json = json.loads(json_str)
print(answer_json)
print(answer_json['type'])