from typing import Any, Dict

import arrow
from rsserpent.utils import HTTPClient, cached

from ..random_ua import get_user_agent


path = "/bilibili/user/{uid}/video"


@cached
async def provider(uid: int) -> Dict[str, Any]:
    """订阅 up 上传的最新视频."""
    user_info_api = f"https://api.bilibili.com/x/space/acc/info?mid={uid}&jsonp=jsonp"
    video_list_api = (
        f"https://api.bilibili.com/x/space/arc/search?mid={uid}&ps=30"
        "&tid=0&pn=1&keyword=&order=pubdate&jsonp=jsonp"
    )

    headers = {
        'User-Agent': get_user_agent()
    }
    async with HTTPClient() as client:
        user_info = (await client.get(user_info_api, headers=headers)).json()
        video_list = (await client.get(video_list_api, headers=headers)).json()

    print(user_info)
    username = user_info["data"]["name"]

    return {
        "title": f"{username}的最新投稿视频",
        "link": f"https://space.bilibili.com/{uid}/video",
        "description": user_info["data"]["sign"],
        "items": [
            {
                "title": item["title"],
                "description": item["description"],
                "link": f"https://www.bilibili.com/video/{item['bvid']}",
                "pub_date": arrow.get(item["created"]),
                "author": username,
            }
            for item in video_list["data"]["list"]["vlist"]
        ],
    }
