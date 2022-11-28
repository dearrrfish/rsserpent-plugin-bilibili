from typing import Any, Dict, Optional

from rsserpent.utils import HTTPClient, cached


HTTPX_CLIENT: Optional[HTTPClient] = None
BILIBILI_COOKIES: Optional[Dict[str, Any]] = None
BVID_TIME = 1589990400
USER_INFO_CACHE_EXPIRE = 60 * 60 * 24


# embedded video
def embed_video(disable_embed: Any, aid: int, page: str, bvid: str) -> str:
    """Get HTML code for embedded video."""
    if disable_embed:
        return ""
    return (
        '<br><iframe src="https://player.bilibili.com/player.html?' f"bvid={bvid}"
        if bvid
        else f"aid={aid}" f"&page={page}"
        if page
        else ""
        '&high_quality=1"'
        ' width="650" height="477" scrolling="no" border="0" frameborder="no"'
        ' framespacing="0" allowfullscreen="true"></iframe>'
    )


def get_video_link(created: int, aid: int, bvid: str) -> str:
    """Method to construct video link, prefer AV to BV."""
    vid = bvid if created > BVID_TIME and bvid else f"av{aid}"
    return f"https://www.bilibili.com/video/{vid}"


async def init_client() -> HTTPClient:
    """Init a httpx client by request Bilibili homepage, in order to obtain cookies."""
    global HTTPX_CLIENT
    global BILIBILI_COOKIES

    HTTPX_CLIENT = HTTPClient()
    if BILIBILI_COOKIES is not None:
        HTTPX_CLIENT.cookies.update(BILIBILI_COOKIES)
        return HTTPX_CLIENT

    await HTTPX_CLIENT.get(
        "https://bilibili.com/", follow_redirects=True
    )  # type: ignore[call-arg]

    BILIBILI_COOKIES = dict(HTTPX_CLIENT.cookies)

    return HTTPX_CLIENT


async def get_client() -> HTTPClient:
    """Get http client instance from global variable."""
    return HTTPX_CLIENT or await init_client()


async def reset_client() -> None:
    """Close http client instance and reset global variable."""
    global HTTPX_CLIENT
    if type(HTTPX_CLIENT) is HTTPClient:
        await HTTPX_CLIENT.aclose()
    HTTPX_CLIENT = None


async def get_api(url: str) -> Dict[str, Any]:
    """Request wrapper to avoid anti-crawler process."""
    data = {}
    headers = {
        "Referer": "https://space.bilibili.com/",
    }
    client = await get_client()
    data = (await client.get(url, headers=headers)).json()
    await reset_client()

    if "code" in data and data.code is not 0:
        raise Exception(f"invalid response for `{url}`")

    return data


@cached
async def get_user_info(uid: int) -> Dict[str, Any]:
    """Cached request fetching user info."""
    return await get_api(
        f"https://api.bilibili.com/x/space/acc/info?mid={uid}&jsonp=jsonp"
    )
