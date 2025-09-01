import json
import re
import unicodedata

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
        question_normalized = unicodedata.normalize('NFC', question.lower())
        print(f"Normalized user question: '{question_normalized}'")
        for kw, trigger_id in self.keyword_list:
            kw_normalized = unicodedata.normalize('NFC', kw.lower())
            print(f"Checking normalized keyword: '{kw_normalized}' with trigger_id: '{trigger_id}'")
            if ' ' in kw_normalized.strip():
                if kw_normalized in question_normalized:
                    print(f"Matched phrase: '{kw}' in question: '{question}'")
                    return trigger_id, kw
            else:
                pattern = r'\b' + re.escape(kw_normalized) + r'\b'
                if re.search(pattern, question_normalized):
                    print(f"Matched word: '{kw}' in question: '{question}'")
                    return trigger_id, kw
        print(f"No match found for question: '{question}'")
        return None, None
