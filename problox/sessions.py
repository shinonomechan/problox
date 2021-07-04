from .clients import Client
from .utils import random_user_agent, hostname_from_url, get_latest_client_path
from .exceptions import *
from http.cookiejar import MozillaCookieJar
from urllib.parse import urlencode
from requests.structures import CaseInsensitiveDict
import json as jsonlib
import re
import requests

class Session:
    def __init__(self, user_agent=random_user_agent(), proxy_url=None):
        self._under_13 = False
        self._csrf_token = None
        self._http = requests.Session()
        self._http.timeout = 30

        self.set_user_agent(user_agent)
        self.set_proxy(proxy_url)

    @classmethod
    def from_cookiefile(cls, cookiefile, *args, **kwargs):
        """Constructs Problox instance with provided cookiejar file."""
        cookiejar = MozillaCookieJar(cookiefile)
        cookiejar.load()
        ins = cls(*args, **kwargs)
        ins.set_cookiejar(cookiejar)
        return ins

    def request(self, method, url, json=None, data=None, headers=None, _retry=None, **kwargs):
        """Wraps `requests.Session.request` with Roblox stuff."""
        if _retry and _retry > 3:
            raise ProbloxException(f"Too many retries while sending request to {url}")

        _retry = _retry if _retry is not None else 0
        headers = CaseInsensitiveDict(headers if headers is not None else {})
        headers.update({
            "Origin": f"https://{'web' if self._under_13 else 'www'}.roblox.com",
            "Referer": f"https://{'web' if self._under_13 else 'www'}.roblox.com/"
        })

        if self._under_13 and hostname_from_url(url) == "www.roblox.com":
            # avoid redirects to web.roblox.com by directly requesting it
            url = re.sub(r"www\.roblox\.com", r"web.roblox.com", url,
                         count=1, flags=re.IGNORECASE)

        if self._csrf_token and method in ("POST", "PUT", "PATCH", "DELETE"):
            headers["X-CSRF-TOKEN"] = self._csrf_token

        if json is not None:
            # serialize json in a more browser-like way
            data = jsonlib.dumps(json, separators=(",", ":"))
            headers["Content-Type"] = "application/json;charset=UTF-8"
        
        response = self._http.request(method, url, data=data, headers=headers,
                                      **kwargs)
        if not self._under_13 \
                and hostname_from_url(response.url) == "web.roblox.com":
            # remember under-13 status to avoid redirects in future requests
            self._under_13 = True
        
        if response.url.endswith("/not-approved"):
            # raise error for punishment page
            raise WebError(f"Redirected to {response.url}")
        
        if "x-csrf-token" in response.headers:
            # set new csrf token and re-send request
            self._csrf_token = response.headers["x-csrf-token"]
            return self.request(method, url, json=json, data=data,
                                headers=headers, _retry=_retry+1, **kwargs)
        
        try:
            # raise exception for error returned (if any)
            for err in response.json().get("errors", []):
                raise APIError(
                    code=err["code"], message=err["message"],
                    response=response)
        except jsonlib.JSONDecodeError:
            pass

        return response

    def join_game(self, place_id, **kwargs):
        """Join game and return client instance."""
        return self._launch_client(
            join_script_url=self._build_join_script_url({
                "request": "RequestGame",
                "browserTrackerId": self.get_browser_tracker_id(),
                "placeId": place_id,
                "isPlayTogetherGame": "false"
            }),
            **kwargs)

    def join_game_server(self, place_id, job_id, **kwargs):
        """Join game server and return client instance."""
        return self._launch_client(
            join_script_url=self._build_join_script_url({
                "request": "RequestGameJob",
                "browserTrackerId": self.get_browser_tracker_id(),
                "placeId": place_id,
                "gameId": job_id,
                "isPlayTogetherGame": "false"
            }),
            **kwargs)

    def join_private_game_server(self, place_id, access_code, link_code=None, **kwargs):
        """Join private game server and return client instance."""
        return self._launch_client(
            join_script_url=self._build_join_script_url({
                "request": "RequestPrivateGame",
                "browserTrackerId": self.get_browser_tracker_id(),
                "placeId": place_id,
                "accessCode": access_code,
                "linkCode": link_code or "",
                "isPlayTogetherGame": "false"
            }),
            **kwargs)
    
    def set_user_agent(self, user_agent):
        """Set user agent to be used for requests."""
        self._http.headers["User-Agent"] = user_agent

    def set_proxy(self, proxy_url):
        """Set proxy to be used for requests."""
        self._http.proxies = {"http": proxy_url, "https": proxy_url}

    def set_cookiejar(self, cookiejar):
        """Set cookiejar to be used for requests."""
        self._http.cookies = cookiejar
    
    def save_cookiejar(self, filename=None):
        if filename:
            self._http.cookies.filename = filename
        self._http.cookies.save()

    def get_cookie(self, name):
        """Find cookie and return it's value, else return None."""
        return self._http.cookies.get(name)

    def get_browser_tracker_id(self):
        """Find and return browser tracker id, else return None."""
        value = self.get_cookie("RBXEventTrackerV2")
        if value:
            return re.search(r"browserid=([^&]*)", value).group(1)

    def _build_join_script_url(self, params):
        """Build and return join script url using provided params."""
        return "https://assetgame.roblox.com/game/PlaceLauncher.ashx?" + urlencode(params)

    def _launch_client(self, join_script_url, client_path=get_latest_client_path(), locale="en_us"):
        auth_ticket = self.request(
            method="POST",
            url="https://auth.roblox.com/v1/authentication-ticket/",
            json={}).headers["rbx-authentication-ticket"]
        client = Client(
            client_path=client_path,
            auth_ticket=auth_ticket,
            join_script_url=join_script_url,
            browser_tracker_id=self.get_browser_tracker_id(),
            locale=locale
        )
        client.start()
        return client