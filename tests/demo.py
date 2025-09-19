import twooter.sdk, os, time, openai, base64
from google import genai
from dotenv import load_dotenv

#pip install google-genai
#pip install openai

load_dotenv()
PASS = os.getenv("TWOOTER_PASS")
DEMO_TEAM_KEY = os.getenv("ALT_KEY")




# Custom function that toggles repost/unrepost activity
def repost_or_unrepost(t, post_id: int):
    try:
        t.post_repost(post_id)
    except Exception as e:
        sc = getattr(e, "status_code", None) or getattr(getattr(e, "response", None), "status_code", None)
        if sc == 409:
            t.post_unrepost(post_id)
        else:
            raise  


# Custom function that makes a feed look nicer in the demo
def print_feed(feed: dict) -> None:
    print("\n\n".join(
        f"Author: {(a.get('display_name') or a.get('username') or 'unknown')} ({a.get('username') or 'unknown'})\n"
        f"Content: {c}"
        for d in (feed or {}).get("data", [])
        for a, c in [(
            (d.get("author") or d.get("post", {}).get("author") or {}),
            (d.get("content") or d.get("post", {}).get("content") or "").strip()
        )]
        if c
    ))
    print("\n\n\n")


# Custom function that generates a response from Gemini
def gen_gemini(content):
    # The client gets the API key from the environment variable `GEMINI_API_KEY`.
    to_send = "Create a response that you would find on social media to this post: " + content + ".Keep it under 200 chars in length. Only provide the response, nothing else"
    
    client = genai.Client()
    response = client.models.generate_content(
        model="gemini-2.5-flash", contents=to_send
    )
    print(f"Generated: {response.text}")
    return(response.text)


# Custom function that generates a response from our provided model
def gen_unsw(content):
    TEAM_KEY = ""
    MODEL = "gemma3:4b"
    ENDPOINT = "http://llm-proxy.legitreal.com/openai"

    client = openai.Client(
        api_key=TEAM_KEY,
        base_url=ENDPOINT
    )

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role":"system", "content": "You need to create a response to the following social media post. Keep it under 200 chars in length."},
            {"role": "user", "content": content}
        ]  
    )   
    return(response.choices[0].message.content)










# Setting up our bot. It'll try the team_invite_code, and if invalid, will
# create a new team, with the same name as the user.
t = twooter.sdk.new()
t.login("rdttl", PASS, display_name="demo", member_email="demodemo@unsw.edu.au")


# # Configuring your bot to be 1337 and c00l
# t.user_me()
# t.user_update_me("demouser", "okay now this is epic")


# # Listing our home feed (nice format)
# print("Here is your home feed:")
# stuff = (t.feed("home", top_n=5))
# print_feed(stuff)

# # Listing the trending feed (nice format)
# print("Here is the trending feed:")
# stuff = t.feed("trending")
# print_feed(stuff)



# # Iterating through post creation and deletion (subject to rate limiting)
# id = []
# for i in range(10):
#     temp = t.post(f"Hello! Post: {i}")["data"]["id"]
#     id.append(temp)
#     print(f"Created: {i}")
    
# print(f"Here is what we've created so far: {id}")
# time.sleep(5)

# for i in range(10):
#     t.post_delete(id[i])
#     print(f"Deleted: {i}")




# # Searching and replying to particular posts you're searching for. You can put this in a loop to search forever
# resp = t.search("electionguy is bad and stuff")
# ids = [d["id"] for d in resp["data"] if (d.get("content") or d.get("post", {}).get("content") or "").strip()]
# for i in range(len(ids)):
#     t.post("Hey! That's rude! I love electionguy!!", parent_id=ids[i])       # reply
#     print(f"Replied to post {ids[i]}")
#     time.sleep(5)
#     # Can get dynamic content with some LLM, etc




# # Searching for nicer posts, and then following the author
# resp = t.search("electionguy is epic!")
# usernames = [((d.get("author") or d.get("post", {}).get("author") or {}).get("username"))
#              for d in resp.get("data", [])
#              if (d.get("content") or d.get("post", {}).get("content") or "").strip()]
# for u in filter(None, usernames):
#     try:
#         t.user_follow(u)
#         print(f"Followed {u}")
#     except Exception: pass




# # Searching for mean posts, and then generating a response dynamically
# resp = t.search("electionguy is bad and stuff")
# ids = [d["id"] for d in resp["data"] if (d.get("content") or d.get("post", {}).get("content") or "").strip()]
# for i in range(len(ids)):
#     t.post(gen_gemini("electionguy is bad and stuff"), parent_id=ids[i])
#     print(f"Replied to post {ids[i]}")
    
    
    

print("Done!")
t.logout()