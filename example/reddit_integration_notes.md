# Auto-Posting to reddit

## Some things to note:
- In the docs, I believe a "link" is what a post is referred to as
- Most calls to the api require either a modhash or outh token
- reddit's JSON data structures: https://github.com/reddit-archive/reddit/wiki/JSON
- reddit's OAuth2: https://github.com/reddit-archive/reddit/wiki/OAuth2-App-Types
- To request commercial access, research approval, or to reach out to the team, please contact us here: https://reddithelp.com/hc/en-us/requests/new?ticket_form_id=14868593862164
- You must use a User-Agent where possible. Change your client's User-Agent string to something unique and descriptive, including the target platform, a unique application identifier, a version string, and your username as contact information, in the following format: ```<platform>:<app ID>:<version string> (by /u/<reddit username>)```
  - Many default User-Agents (like "Python/urllib" or "Java") are drastically limited to encourage unique and descriptive user-agent strings.
  - Including the version number and updating it as you build your application allows us to safely block old buggy/broken versions of your app.
  - NEVER lie about your User-Agent. 

### modhashes
A modhash is a token that the reddit API requires to help prevent CSRF. Modhashes can be obtained via the /api/me.json call or in response data of listing endpoints.

The preferred way to send a modhash is to include an X-Modhash custom HTTP header with your requests.

Modhashes are not required when authenticated with OAuth.

### response body encoding
For legacy reasons, all JSON response bodies currently have <, >, and & replaced with &lt;, &gt;, and &amp;, respectively. If you wish to opt out of this behaviour, add a raw_json=1 parameter to your request.

### Rate limits

Monitor the following response headers to ensure that you're not exceeding the limits:

- X-Ratelimit-Used: Approximate number of requests used in this period
- X-Ratelimit-Remaining: Approximate number of requests left to use
- X-Ratelimit-Reset: Approximate number of seconds to end of period

We enforce rate limits for those eligible for free access usage of our Data API. The limit is:   

100 queries per minute (QPM) per OAuth client id. Traffic not using OAuth or login credentials will be blocked, and the default rate limit will not apply.

## Creating a Post

I believe this is the api we need to hit to create a post on a given subreddit
https://www.reddit.com/dev/api/#POST_api_submit

Info from the link is as follows:

POST /api/submit
Submit a link to a subreddit.
Submit will create a link or self-post in the subreddit sr with the title title. If kind is "link", then url is expected to be a valid URL to link to. Otherwise, text, if present, will be the body of the self-post unless richtext_json is present, in which case it will be converted into the body of the self-post. An error is thrown if both text and richtext_json are present.
extension is used for determining which view-type (e.g. json, compact etc.) to use for the redirect that is generated after submit.

ad	                        boolean value
api_type	                the string json
app	
collection_id	            (beta) the UUID of a collection
extension	                extension used for redirectsflair_id	
flair_id                    a string no longer than 36 charactersflair_text	
flair_text                  a string no longer than 64 charactersg-recaptcha-response	
kind	                    one of (link, self, image, video, videogif)
nsfw	                    boolean value
post_set_default_post_id	a string
post_set_id	                a string
recaptcha_token	            a string
resubmit	                boolean value
richtext_json	            JSON data
sendreplies	                boolean value
spoiler	                    boolean value
sr	                        subreddit name
text	                    raw markdown text
title	                    title of the submission. up to 300 characters long
uh / X-Modhash header	    a modhash
url	                        a valid URL
video_poster_url	        a valid URL

More information can be found here: https://github.com/reddit-archive/reddit/wiki/API:-submit

