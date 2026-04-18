def extract_seller_name(html, expected_seller):
    try:
        html_lower = html.lower()
        expected = expected_seller.lower().strip()

        # ✅ 1. priority: sheet seller match check
        if expected and expected in html_lower:
            return expected_seller

        # ✅ 2. real seller extraction
        import re
        patterns = [
            r"sold by[:\s]*([a-zA-Z0-9\s\-&\.]+)",
            r"seller[:\s]*([a-zA-Z0-9\s\-&\.]+)",
            r"by[:\s]*([a-zA-Z0-9\s\-&\.]+)"
        ]

        for pattern in patterns:
            match = re.search(pattern, html_lower)
            if match:
                return match.group(1).strip()

        return ""

    except:
        return ""
