import os
import aiohttp

from aiohttp import web

from gidgethub import routing, sansio
from gidgethub import aiohttp as gh_aiohttp

router = routing.Router()


@router.register("issues", action="opened")
async def issue_opened_event(event, gh, *args, **kwargs):
    """
    Whenever an issue is opened, greet the author and say thanks.
    """
    url = event.data["issue"]["comments_url"]
    author = event.data["issue"]["user"]["login"]

    message = f"Thanks for the report @{author}! I will look into it ASAP! (I'm a bot)."
    await gh.post(url, data={"body": message})


# Webhook event name: issue_comment
# Resource: https://developer.github.com/v3/activity/events/types/#webhook-event-name-15
@router.register("issue_comment", action="created")
async def react_to_issue_comment(event, gh, *args, **kwargs):
    """
    Whenever an issue is comments, react to it .
    """
    url = event.data["comment"]["url"]+"/reactions"

    await gh.post(url,
                  data={"content": "heart"},
                  accept='application/vnd.github.squirrel-girl-preview+json')


# Any issue that is created, set its assignee
# POST /repos/:owner/:repo/issues/:number/assignees
@router.register("issues", action="opened")
async def add_assignee_to_issue(event, gh, *args, **kwargs):
    """
    Whenever an issue is created, assign it to alijafargholi.
    """
    url = event.data["issue"]["url"]+"/assignees"
    print(f"This is the new url {url}")

    await gh.post(url,
                  assignees=['alijafargholi'],
                  accept='application/vnd.github.symmetra-preview+json')


async def main(request):
    body = await request.read()

    secret = os.environ.get("GH_SECRET")
    oauth_token = os.environ.get("GH_AUTH")

    event = sansio.Event.from_http(request.headers, body, secret=secret)
    async with aiohttp.ClientSession() as session:
        gh = gh_aiohttp.GitHubAPI(session, "mariatta",
                                  oauth_token=oauth_token)
        await router.dispatch(event, gh)
    return web.Response(status=200)


if __name__ == "__main__":
    app = web.Application()
    app.router.add_post("/", main)
    port = os.environ.get("PORT")
    if port is not None:
        port = int(port)

    web.run_app(app, port=port)
