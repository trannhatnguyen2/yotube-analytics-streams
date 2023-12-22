import json
import logging
from loguru import logger

from pprint import pprint
import requests 
from kafka import KafkaProducer

from constants import YOUTUBE_API_KEY, PLAYLIST_ID


def fetch_page(url, parameters, page_token=None):
    params = {**parameters, 'key': YOUTUBE_API_KEY, 'page_token': page_token}
    response = requests.get(url,params)
    payload=json.loads(response.text)

    # logging.info('Response => %s', payload)
    logger.info('Response => %s', payload)

    return payload


def fetch_page_lists(url, parameters, page_token=None):
    while True:
        payload = fetch_page(url, parameters, page_token)
        yield from payload['items']

        page_token = payload.get('nextPageToken')
        if page_token is None:
            break


def format_response(video):
    video_res = {
        'title': video['snippet']['title'],
        'likes': int(video['statistics'].get('likeCount', 0)),
        'comments': int(video['statistics'].get('commentCount', 0)),
        'views': int(video['statistics'].get('viewCount', 0)),
        'favorites': int(video['statistics'].get('favoriteCount', 0)),
        'thumbnail': video['snippet']['thumbnails']['default']['url']
    }

    return video_res


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # logger.info("START")

    producer = KafkaProducer(bootstrap_servers=['localhost:9092'])

    for video_item in fetch_page_lists(
        "https://www.googleapis.com/youtube/v3/playlistItems",
            {
                'playlistId': PLAYLIST_ID,
                'part': 'snippet,contentDetails,status'
            },
            None
    ):
        # get all video_id in page_list
        video_id = video_item['contentDetails']['videoId']

        for video in fetch_page_lists(
            "https://www.googleapis.com/youtube/v3/videos",
            {
                'id': video_id,
                'part': 'snippet,statistics'
            },
            None
        ):
            # logging.info("Video here => %s", pprint(video))

            # logger.info('Video here => %s', pprint(format_response(video)))

            producer.send('youtube_videos', json.dumps(format_response(video)).encode('utf-8'), key=video_id.encode('utf-8'))
            # producer.flush()

            print('Sent ', video['snippet']['title'])



    # response = requests.get("https://www.googleapis.com/youtube/v3/videos",
    #                         {
    #                             'key': YOUTUBE_API_KEY,
    #                             'id': 'jk7LbXUpmz0',
    #                             'part': 'snippet,statistics,status'
    #                         })

    # response = json.loads(response.text)['items']

    # for video in response:
    #     video_res = {
    #         'title': video['snippet']['title'],
    #         'likes': int(video['statistics'].get('likeCount', 0)),
    #         'comments': int(video['statistics'].get('commentCount', 0)),
    #         'views': int(video['statistics'].get('viewCount', 0)),
    #         'favorites': int(video['statistics'].get('favoriteCount', 0)),
    #         'thumbnail': video['snippet']['thumbnails']['default']['url']
    #     }

    #     print(pprint(video_res))

    #     producer.send('youtube_videos', json.dumps(video_res).encode('utf-8'))
    #     producer.flush()


    # response = requests.get("https://www.googleapis.com/youtube/v3/playlistItems",
    #                         {
    #                             'key': YOUTUBE_API_KEY,
    #                             'playlistId': PLAYLIST_ID,
    #                             'part': 'snippet,contentDetails,status',
    #                             'page_token': 'EAAajQFQVDpDQVVpRURFeVJVWkNNMEl4UXpVM1JFVTBSVEVvQVVqZW9zcWV2WW41QWxBQldrUWlRMmxLVVZSSGJIWk5la0oyVVRCRk1GTlVUbXRQVjNSdVZWZFdlbGR1YUdaVE1scDBVMGRhUlZSSFZsRk9SMFkyUldkelNUSTBXR3RzWjFsUmMwcExhMFJCSWc'
    #                         })

    # print(response.text)
