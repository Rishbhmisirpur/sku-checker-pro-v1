import openai

openai.api_key = "YOUR_OPENAI_API_KEY"

def ai_sku_match(page_text, sku):
    try:
        prompt = f"""
        Check if this SKU: {sku}
        exists or is semantically similar in the following content:

        {page_text[:2000]}

        जवाब sirf YES ya NO me do.
        """

        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        answer = response.choices[0].message.content.strip().lower()
        return "yes" in answer

    except:
        return False
