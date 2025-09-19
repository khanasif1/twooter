import twooter.sdk

def repost_or_unrepost(t, post_id: int):
    try:
        t.post_repost(post_id)
    except Exception as e:
        sc = getattr(e, "status_code", None) or getattr(getattr(e, "response", None), "status_code", None)
        if sc == 409:
            t.post_unrepost(post_id)
        else:
            raise

t = twooter.sdk.new()
t.login("rdttl", "rdttlrdttl", display_name="rdttl", member_email="rdttl@proton.me")

t.user_get("rdttl")
t.user_me()
t.user_update_me("RDTTL", "I used the SDK to change this!")
t.user_activity("rdttl")
t.user_follow("admin")
t.user_unfollow("admin")

post_id = t.post("Hello, world! 123123123 @rdttl")["data"]["id"]
print(t.search("Hello, world! 123123123 @rdttl"))
t.post_delete(post_id)
print(t.search("Hello, world! 123123123 @rdttl"))

t.notifications_list()
t.notifications_unread()
t.notifications_count()
t.notifications_count_unread()

t.feed("trending")
t.feed("home", top_n=1)

t.post_like(123)
t.post_unlike(123)
repost_or_unrepost(t, 123)
print(t.post_get(123))
print(t.post_replies(123))

t.logout()
