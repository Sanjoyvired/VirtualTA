import openai
openai.api_key = "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"


def getReview(assignment, solution):
    prompt = f"you are a teaching assistant who provides assignment review. Please read the assignment {assignment} and the submission of the assignment in json format is {solution}"
    outputFormat = "I need the output where following things can be placed 1. score out of 25 2. Detailed personalized Feedback and also skill level mapping from 1 to 5 in below format"
    jsonFormat = """{
        "Feedback Score":20,
        "Detailed Feedback":"Detailed Feedback",
        "Submitted code":"Old code",
        "Ideal Code":"Ideal code",
        "Skills":[{"html":5},{"Javascript":3}]

        """

    result = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[

            {"role": "user", "content": prompt},
            {"role": "user", "content": outputFormat},
            {"role": "user", "content": jsonFormat},
        ]
    )
    print(result)
    return result.choices[0].message.content
