from openai import OpenAI

client = OpenAI()

def judge_trace(trace: str) -> str:
    response = client.beta.parse.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": f"Judge the following trace: {trace}"}],
        temperature=0.5
    )
    return response.choices[0].message.content