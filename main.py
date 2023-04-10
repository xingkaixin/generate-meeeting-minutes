from pathlib import Path

import openai

from config import openai_config


def read_srt(srt_file):
    with srt_file.open(mode="r", encoding="utf-8") as f:
        srt = f.read()

    lines = srt.strip().split("\n")
    subs = []
    sub = {}

    for i, line in enumerate(lines):
        if i % 4 == 0:
            if sub.get("id", None) is not None:
                subs.append(sub)
            sub = {"id": int(line)}
        elif i % 4 == 1:
            start, end = line.split(" --> ")
            sub["start"] = start
            sub["end"] = end
        elif i % 4 == 2:
            sub["text"] = line

    if sub is not None:
        subs.append(sub)
    return subs


def split_ask_answer(subs):
    subarrays = [subs[i : i + 100] for i in range(0, len(subs), 100)]  # noqa

    answer = []

    for subarray in subarrays:
        sub_question = "\n".join([sub["text"] for sub in subarray])
        quesiton = "仔细阅读以下内容，我要用于撰写会议纪要.\n" f"{sub_question}\n"

        answer.append(ask_ai(quesiton))

    return answer


def ask_ai(question):
    openai.api_key = openai_config.key
    openai.api_base = openai_config.base_url
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": question}],
        temperature=0.3,
        max_tokens=2048,
    )
    if "choices" in response:
        return (
            response["choices"][0].get("message").get("content").encode("utf8").decode()
        )
    else:
        raise ValueError("Invalid response from ChatGPT")


def main():
    srt_file = Path("./data/20230410.wav.srt")
    subs = read_srt(srt_file)
    answers = "\n".join(split_ask_answer(subs))
    question = f"仔细阅读下面的内容，生成一份有着10年经验的项目经理会议纪要。\n {answers}"
    print(ask_ai(question))


if __name__ == "__main__":
    main()
