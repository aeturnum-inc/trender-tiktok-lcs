from flask import Flask, request
import json
import datetime

from config import NO_ACTION, LIKE, LIKE_OR_COMMENT, COMMENT

app = Flask(__name__)

with open('data/profile_ranking.json', 'r') as f:
    profile_ranking = json.load(f)

with open('data/tiktok_posts.json', 'r') as f:
    profile_posts = json.load(f)

profile_ranking.sort(key=lambda x: x['score'], reverse=True)

@app.route('/', methods=['POST'])
def index():
    request_json = request.get_json()
    member_id, topic_id = request_json['member_id'], request_json['topic_id']

    top_profiles = list()

    for profile in profile_ranking:
        if profile['member_id'] == member_id and profile['topic_id'] == topic_id:
            # get first 5 profiles and append to top_profiles
            top_profiles.append(profile['profile'])
            if len(top_profiles) == 5:
                break

    # get posts for each profile
    final_response = list()
    for post in profile_posts:
        if (post['screen_name'] not in top_profiles):
            continue
        # check post is not older than 48 hours
        if (datetime.datetime.now() - datetime.datetime.strptime(post['tiktok_created_at'], '%d/%m/%Y %H:%M:%S')).days > 2:
            continue
        
        attributes = post["attributes"]
        # check if atributes has key like_count
        if "like_count" in attributes.keys():
            like_or_view_count = attributes["like_count"]
        else:
            like_or_view_count = attributes['view_count']

        comments_count = post['attributes']['comment_count']

        recommended_action = NO_ACTION

        if (comments_count == 0 ):
            recommended_action = LIKE
        elif (like_or_view_count == 0):
            recommended_action = COMMENT
        else:
            ratio = like_or_view_count/comments_count
            if ratio >= 2:
                recommended_action = LIKE
            elif ratio <= 1:
                recommended_action = COMMENT
            else:
                recommended_action = LIKE_OR_COMMENT

        OBJ = {
            "member_id": member_id,
            "topic_id": topic_id,
            "post_id": post['tiktok_id'],
            "screen_name": post['screen_name'],
            "recommended_action": recommended_action,
        } 
        final_response.append(OBJ)

    return json.dumps(final_response)


