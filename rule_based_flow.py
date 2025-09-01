import json
import re

class RuleBasedFlow:
    def __init__(self, flow_json='codeware_bot_flow.json'):
        with open(flow_json, 'r', encoding='utf-8') as f:
            flows = json.load(f)
        self.keyword_list = []
        for flow in flows:
            keywords = flow.get('keywords', [])
            trigger_id = flow.get('id')
            for kw in keywords:
                self.keyword_list.append((kw.lower(), trigger_id))

    def check_trigger(self, question):
        question_lower = question.lower()
        for kw, trigger_id in self.keyword_list:
            kw_lower = kw.lower()
            if ' ' in kw_lower.strip():
                if kw_lower in question_lower:
                    return trigger_id, kw
            else:
                pattern = r'\b' + re.escape(kw_lower) + r'\b'
                if re.search(pattern, question_lower):
                    return trigger_id, kw
        return None, None
