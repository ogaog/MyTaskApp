import datetime
import ast
import os
from os.path import join, dirname, abspath

from dotenv import load_dotenv
from googleapiclient.discovery import build
from google.auth import load_credentials_from_file
import openai

# 同ディレクトリ下の.envファイルに保存されているgoogle calendarのidとChatGPTのAPIを取得する.
dotenv_path = join(dirname(abspath("__file__")), '.env')
load_dotenv(dotenv_path)
MY_CALENDAR_ID = os.getenv("MY_CALENDAR_ID")
openai.api_key = os.getenv("OPENAI_APIKEY")

# googleのAPIを使う用意をする.
SCOPES = ['https://www.googleapis.com/auth/calendar']
creentialds = load_credentials_from_file('credentials_service.json', SCOPES)[0]
service = build('calendar', 'v3', credentials=creentialds)

# window.pyで使用する,APIを利用する関数を作成していく
def get_events():
    """現在時刻以降に始まるイベント情報を取得する.

    Returns:
        None: イベントが存在しなかった場合Noneが返される.
        dict: イベントが存在する場合,日付(yyyy-mm-dd)がkey,その日付に始まるイベントが
        格納されたリストがvalueとなる辞書events_dictが返される.
    """    
    now = datetime.datetime.utcnow().isoformat() + 'Z'

    # カレンダー上のイベント情報を取得
    events_result = service.events().list(
        calendarId=MY_CALENDAR_ID, 
        timeMin=now, 
        maxResults=70, 
        singleEvents=True,
        orderBy='startTime'
        ).execute()  
    events = events_result.get('items', []) # eventsは取得したイベント情報(dict型)が格納されたリストである.

    if not events:
        return None
    else:
        events_dict = {}
        for event in events:
            # イベントの開始日付(yyyy-mm-dd)を取得し,同じ日付のところのリストにイベントを追加していく.
            date = event['start'].get('dateTime', event['start'].get('date'))[:10]
            if date in events_dict:
                events_dict[date] += [event]
            else:
                events_dict[date] = [event]
        return events_dict
    
def switch_done(event):
    """イベント(タスク)の完了,未完了状態を切り替える.
    タスクが終わっているかどうかは,イベント情報の'transparency'の値で記録する.
    イベントの'transparency'の値が'transparent'(完了状態)か'opaque'(未完了状態)の
    どちらなのかを調べ,反転させる.

    Args:
        event (dict): 一つのイベント情報が記録されている辞書.

    Returns:
        dict: カレンダー上のイベントの'transparency'の値を変更し,
        アップデートされたイベント情報updated_eventが返される.
    """    
    event_id = event['id']

    # デフォルトのイベント情報では'transparency'というkeyが存在しないため'opaque'を取得することになる.
    current_transparency = event.get('transparency', 'opaque')

    new_transparency = 'transparent' if current_transparency == 'opaque' else 'opaque' # 状態を反転.
    event['transparency'] = new_transparency

    # カレンダー上のイベント情報を変更する
    updated_event = service.events().update(
        calendarId=MY_CALENDAR_ID, 
        eventId=event_id, 
        body=event
        ).execute()
    return updated_event

def edit_event(event):
    """イベントの内容を変更する.

    Args:
        event (dict): 内容が書き換えられているイベント情報.

    Returns:
        dict: カレンダー上のイベントの内容を変更し,アップデートされたイベント情報updated_eventが返される.
    """    
    event_id = event['id']
    
    # カレンダー上のイベント情報を変更する
    updated_event = service.events().update(
        calendarId=MY_CALENDAR_ID, 
        eventId=event_id, 
        body=event
        ).execute()
    return updated_event

def delete_event(event):
    """イベントを削除する.

    Args:
        event (dict): 削除するイベントの情報.イベント情報からidを取得し,カレンダー上のイベントを削除する.

    Returns:
        str: 完了メッセージが返される.
    """    
    # カレンダー上のイベントを削除
    service.events().delete(calendarId=MY_CALENDAR_ID, eventId=event['id']).execute()
    return f"Event with ID {event['id']} has been deleted."
    
def add_event(event):
    """イベントを追加する.

    Args:
        event (dict): 追加するイベントの情報.

    Returns:
        dict: 追加したイベントの情報added_eventが返される.
    """    
    # イベントを追加
    added_event = service.events().insert(calendarId=MY_CALENDAR_ID, body=event).execute()
    return added_event

def arrange_input(prompt):
    """タスクの内容をChatGPTに渡し,googleカレンダーのイベントとして追加できるように情報を整えてもらう関数.
    例として,"大掃除 12月31日15時 ぞうきん,スプレー買う"というpromptで,
    summary(イベント名):大掃除
    start(開始日時):12-31 12:00
     end (終了日時):12-31 15:00
    description(メモ):ぞうきん,スプレー買う
    というイベント情報(dict)が生成され,返される.
    締め切り日時はendとして,締切日時の3時間前をstartとして設定する.

    Args:
        prompt (str): ChatGPTに渡す入力データ. タスクの内容を「<name><date/time information><memo>」
        という順番の形式で受け取り,<name>はタスクの名前,<date/time information>はタスクの締切日時,
        <memo>はタスクのメモを表す.

    Returns:
        dist: ChatGPTが整えたデータを元に作成したイベント情報が返される.
    """    

    # ChatGPTにpromptを渡し,イベント情報を整えてもらう.
    response = openai.chat.completions.create(
        model = "gpt-3.5-turbo",
        messages = [
            {"role": "system", "content": (
                "You are a program that outputs received data in the appropriate format. "
                "The received data consists of [<name><date/time information><memo>]."
                " You output this data in the format {'summary':'<name>','date':'yyyyy-mm-dd','time':'hh:mm','description':'<memo>','pre3h_date':'yyyyy-mm-dd','pre3h_time':'hh:mm'}."
                f"Note that the date and time to be output are inferred from the <date/time information> and the current time ({datetime.datetime.now()})."
                "The date and time three hours before ('date':'yyyyyy-mm-dd','time':'hh:mm') shall be ('pre3h_date':'yyyyyy-mm-dd','pre3h_time':'hh:mm')."
                "If no time is specified, 23:59 is assumed. If no date is specified, the current date is assumed."
                "If <memo> is not present, 'description':'None' is assumed."
            )},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    # ChatGPTからのメッセージを取得.
    data_msg = response.choices[0].message.content
    format_data = ast.literal_eval(data_msg) # dict型に変換

    # イベント情報としてdraft_eventを作成する.
    draft_event = {
        'summary': f'{format_data["summary"]}',
        'description': f'{format_data["description"]}',
        'start': {
            'dateTime': f'{format_data["pre3h_date"]}T{format_data["pre3h_time"]}:00+09:00'
        },
        'end': {
            'dateTime': f'{format_data["date"]}T{format_data["time"]}:00+09:00'
        }
    }
    return draft_event