from typing import Any, Dict

import arrow
from rsserpent.utils import cached

from ..utils import get_video_link, get_api


path = "/bilibili/user/{uid}/video"


@cached
async def provider(uid: int) -> Dict[str, Any]:
    """订阅 up 上传的最新视频."""
    user_info_api = f"https://api.bilibili.com/x/space/acc/info?mid={uid}&jsonp=jsonp"
    user_info = await get_api(user_info_api)
    username = user_info["data"]["name"]

    video_list_api = (
        f"https://api.bilibili.com/x/space/arc/search?mid={uid}&ps=30"
        "&tid=0&pn=1&keyword=&order=pubdate&jsonp=jsonp"
    )
    video_list = await get_api(video_list_api)

    return {
        "title": f"{username}的最新投稿视频",
        "link": f"https://space.bilibili.com/{uid}/video",
        "description": user_info["data"]["sign"],
        "items": [
            {
                "title": item["title"],
                "description": f'<img src="{item["pic"]}" /><br><p>{item["description"]}</p>',
                "link": get_video_link(item["created"], item["aid"], item["bvid"]),
                "pub_date": arrow.get(item["created"]),
                "author": username,
            }
            for item in video_list["data"]["list"]["vlist"]
        ],
    }
