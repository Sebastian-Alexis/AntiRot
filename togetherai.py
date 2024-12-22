from together import Together
import re

#YOU WILL NEED TO SET ENVIROEMNT VARIABLE (TOGETHER_API_KEY) WITH YOUR API KEY 
#account/api key creating is completley free, and you should never get charged unless you really use a lot in a short amount of time.

client = Together()

def smooth_translation(text):
    prompt = (
        "You are a translator of Gen Alpha/Gen Z slang. "
        "Most words have already been translated, and the translated text is in brackets. "
        "Make these translations natural and smooth. "
        "Make the translations understandable by all audiences and use as little slang as possible in the response. "
        "If necessary, change words that are not in brackets to allow for the translation to make sense in context. "
        "Provide two sections in the response: "
        "1. 'Translation:' followed by the smooth translation text only. "
        "2. 'Explanation:' followed by a justification or explanation of the translation choices made."
    )
    
    try:
        #call Together API for completion - if you havnet used Together API before, its awesome.
        completion = client.chat.completions.create(
            model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": text}
            ],
        )
        response = completion.choices[0].message.content
        translation = explanation = ""
        #response to translation/explanation
        if "Translation:" in response and "Explanation:" in response:
            translation_part, explanation_part = response.split("Explanation:", 1)
            translation = translation_part.replace("Translation:", "").strip()
            explanation = explanation_part.strip()

        #clean up annoying formatting
        translation = re.sub(r"^\**|\**$", "", translation).strip() 
        translation = re.sub(r"\s{2,}", " ", translation) 

        explanation = re.sub(r"^\**|\**$", "", explanation).strip()  #remove asteriks - LLAMA likes this for some reason - might be for formatting reasons? Not sure, but needs to be removed
        explanation = re.sub(r"\s{2,}", " ", explanation)  #cllapse multiple spaces into one

        return translation, explanation
    except Exception as e:
        print(f"Error using Together API: {e}")
        return "An error occurred while refining the translation.", ""
