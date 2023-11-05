import os
import numpy as np
from openai.embeddings_utils import distances_from_embeddings
import pandas as pd
import openai
import requests
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
rapidAPI_key = os.getenv("RAPIDAPI_KEY")


df = pd.read_csv("processed/embeddings.csv", index_col=0)
df["embeddings"] = df["embeddings"].apply(eval).apply(np.array)

df.head()


def create_context(question, df, max_len=1800, size="ada"):
    """
    Create a context for a question by finding the most similar context from the dataframe
    """

    # Get the embeddings for the question
    q_embeddings = openai.Embedding.create(
        input=question, engine="text-embedding-ada-002"
    )["data"][0]["embedding"]

    # Get the distances from the embeddings
    df["distances"] = distances_from_embeddings(
        q_embeddings, df["embeddings"].values, distance_metric="cosine"
    )

    returns = []
    cur_len = 0

    # Sort by distance and add the text to the context until the context is too long
    for i, row in df.sort_values("distances", ascending=True).iterrows():
        # Add the length of the text to the current length
        cur_len += row["n_tokens"] + 4

        # If the context is too long, break
        if cur_len > max_len:
            break

        # Else add it to the text that is being returned
        returns.append(row["text"])

    # Return the context
    return "\n\n###\n\n".join(returns)


def answer_question(
    df,
    question,
    messages,
    max_len=400,
    size="ada",
    debug=False,
):
    """
    Answer a question based on the most similar context from the dataframe texts
    """
    # if rapidAPI_key:
    #     url = "https://nlp-translation.p.rapidapi.com/v1/translate"

    #     querystring = {"text": question, "to": "fr", "from": "en"}

    #     headers = {
    #         "X-RapidAPI-Key": rapidAPI_key,
    #         "X-RapidAPI-Host": "nlp-translation.p.rapidapi.com",
    #     }

    #     response = requests.get(url, headers=headers, params=querystring)
    #     question = response.json()["translated_text"]["fr"]

    context = create_context(
        question,
        df,
        max_len=max_len,
        size=size,
    )
    # If debug, print the raw model response
    if debug:
        print("Context:\n" + context)
        print("\n\n")

    try:
        messages.append(
            {
                "role": "user",
                "content": "Context: "
                + context
                + " \n\n\n Questions: "
                + question
                + ". Answer in english",
            }
        )
        # Create a completions using the question and context
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0,
            max_tokens=512,
            stream=True,
        )

        # create variables to collect the stream of chunks
        collected_chunks = []
        collected_messages = []
        # iterate through the stream of events
        for chunk in response:
            if chunk["choices"][0]["finish_reason"] == None:
                collected_chunks.append(chunk)  # save the event response
                chunk_message = chunk["choices"][0]["delta"]  # extract the message
                collected_messages.append(chunk_message["content"])  # save the message
                print(chunk_message["content"], end="")  # print the delay and text

        response = "".join(collected_messages)
        messages.append(
            {
                "role": "assistant",
                "content": response,
            }
        )
        return messages
    except Exception as e:
        print("Exception:")
        print(e)
        return ""


messages = [
    {
        "role": "system",
        "content": "You are a helpful assistant. your name is EnsetAI. Be helpful to your users. if the question can't be answered based on the context, say that you don't know the answer",
    },
]
while True:
    question = input("Question: ")

    messages = answer_question(df, question, messages, debug=True)
    print("\n")
