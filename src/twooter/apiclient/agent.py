from typing import Any, Dict, Optional


class Agent:
    def __init__(self, username: str, twoots_api, users_api, notifications_api):
        self.username = username
        self._twoots = twoots_api
        self._users = users_api
        self._notifications = notifications_api

    # Posts
    def post(self, content: str, parent_id: Optional[int] = None, embed: Optional[str] = None, media: Optional[list[str]] = None) -> Dict[str, Any]:
        return self._twoots.create(self.username, content, parent_id=parent_id, embed=embed, media=media)

    def like(self, post_id: int) -> Dict[str, Any]:
        return self._twoots.like(self.username, post_id)

    def unlike(self, post_id: int) -> Dict[str, Any]:
        return self._twoots.unlike(self.username, post_id)

    def repost(self, post_id: int) -> Dict[str, Any]:
        return self._twoots.repost(self.username, post_id)

    def unrepost(self, post_id: int) -> Dict[str, Any]:
        return self._twoots.unrepost(self.username, post_id)

    def delete_post(self, post_id: int) -> Dict[str, Any]:
        return self._twoots.delete(self.username, post_id)

    # Social
    def follow(self, target_username: str) -> Dict[str, Any]:
        return self._users.follow(self.username, target_username)

    def unfollow(self, target_username: str) -> Dict[str, Any]:
        return self._users.unfollow(self.username, target_username)

    # Notifications
    def notifications(self) -> Dict[str, Any]:
        return self._notifications.list(self.username)

    def notifications_unread(self) -> Dict[str, Any]:
        return self._notifications.unread(self.username)

    def notifications_count(self) -> Dict[str, Any]:
        return self._notifications.count(self.username)

    def notifications_count_unread(self) -> Dict[str, Any]:
        return self._notifications.count_unread(self.username)

    def mark_read(self, notification_id: int) -> Dict[str, Any]:
        return self._notifications.mark_read(self.username, notification_id)

    def mark_unread(self, notification_id: int) -> Dict[str, Any]:
        return self._notifications.mark_unread(self.username, notification_id)

    def delete_notification(self, notification_id: int) -> Dict[str, Any]:
        return self._notifications.delete(self.username, notification_id)

    def clear_notifications(self) -> Dict[str, Any]:
        return self._notifications.clear(self.username)

