import flet as ft

import serviceApi as sa

# ElevatedButtonで使用する色を設定しておく.
PROP_DONE_BTN_COLOR = {"str_def":'#162229', "str_dis":'#202429', "bg_def":'#7fb4f2', "bg_dis":'#455a64'}# 未完了状態のイベントのボタン,Doneボタンの色
PROP_NOTYET_BTN_COLOR = {"str_def":'#cad6eb', "str_dis":'#686f79', "bg_def":'#253445', "bg_dis":'#33475f'}# 完了状態のイベントのボタン,Not yetボタンの色

def main(page):
    # 関数定義ここから
    def make_elevated_button(text,on_click_act,prop_btn_color):
        """イベントカードを作るボタンとswitch_doneするボタンを作る.

        Args:
            text (str): ボタンに書かれる言葉.
            on_click_act (function): ボタンが押されたときに行う処理.
            prop_btn_color (dict): ボタンの色設定.PROP_DONE_BTN_COLORもしくはPROP_NOTYET_BTN_COLOR

        Returns:
            ElevatedButton: 作成されたボタンが返される.
        """        
        return ft.ElevatedButton(
            text,
            on_click=on_click_act,
            style=ft.ButtonStyle(
                color={
                    ft.MaterialState.DEFAULT: prop_btn_color["str_def"],
                    ft.MaterialState.DISABLED: prop_btn_color["str_dis"]
                },
                bgcolor={
                    ft.MaterialState.DEFAULT: prop_btn_color["bg_def"],
                    ft.MaterialState.DISABLED: prop_btn_color["bg_dis"]
                }
            )
        )      

    def make_add_event_btm_sheet(e):
        """イベントを新規作成するための入力シートを出現させ,入力に応じたイベントを作成する.

        Args:
            e (flet_core.control_event.ControlEvent): この関数をイベントハンドラとして定義するときに必要.
        """     

        # シートを閉じる. キャンセルボタンの処理
        def btn_close_btm_sheet(*,e=None):
            add_event_btm_sheet.open=False
            add_event_btm_sheet.update()

        # 送信ボタンが押されたときの処理
        def btn_send_prompt(*,e=None):
            # alert_dialogで,Cancelボタンが押されたときの処理
            def not_add_event(e):
                alert_dialog.open = False
                main_page.disabled = False
                add_event_column.disabled = False
                page.update()
                add_event_btm_sheet.update()

                btn_close_btm_sheet()

            # alert_dialogで,Addボタンが押されたときの処理
            def do_add_event(e):
                alert_dialog.open = False
                main_page.disabled = True
                page.update()

                # イベントを追加する
                added_event = sa.add_event(draft_event)

                load_days_column()

                main_page.disabled = False
                add_event_column.disabled = False
                page.update()
                add_event_btm_sheet.update()

                btn_close_btm_sheet()

            # 全てのボタン,入力欄を選択不能にする
            main_page.disabled = True
            add_event_column.disabled = True
            page.update()
            add_event_btm_sheet.update()

            # 入力を渡して,イベントとしてのデータを受け取る
            draft_event = sa.arrange_input(prompt_field.value)

            # 受け取ったデータでイベントを作成してよいか確認するアラートダイアログ
            alert_dialog = ft.AlertDialog(
                title=ft.Text("Check event"),
                content=ft.Text(
                    (
                        f"{draft_event['summary']}\n"
                        f"start :{draft_event['start'].get('dateTime')[:16].replace('T',' ')}\n"
                        f" end :{draft_event['end'].get('dateTime')[:16].replace('T',' ')}\n"
                        f"{draft_event['description']}"
                    ),
                    selectable=True
                ),
                actions=[
                    ft.TextButton("Cancel", on_click=not_add_event),
                    ft.TextButton("Add", on_click=do_add_event,style=ft.ButtonStyle(color=ft.colors.LIGHT_BLUE_ACCENT)),
                ],
                actions_alignment=ft.MainAxisAlignment.END
            )

            # アラートダイアログを表示
            page.dialog = alert_dialog
            alert_dialog.open = True
            page.update()

        # 入力欄   
        prompt_field = ft.TextField(
            label="input task data",
            hint_text="<task name>\n<date/time infomation>\n<memo>",
            multiline=True,
            min_lines=3,
            max_lines=5,
            autofocus=True
        )
        
        # 入力欄と送信ボタン,キャンセルボタン
        add_event_column = ft.Column(
            controls=[
                prompt_field,
                ft.Row(controls=[
                    ft.IconButton(ft.icons.SEND,icon_color=ft.colors.BLUE_200,tooltip="send",on_click=lambda e:btn_send_prompt(e=e)),
                    # ft.IconButton(ft.icons.SEND_AND_ARCHIVE,icon_color=ft.colors.BLUE_200,tooltip="send & again"), #連続して予定を作成
                    ft.IconButton(ft.icons.CLOSE,on_click=lambda e:btn_close_btm_sheet(e=e))
                ])
            ]
        )

        # add_event_columnをボトムシートに乗っける
        add_event_btm_sheet = ft.BottomSheet(
            content = ft.Container(
                content=add_event_column,
                padding=15
            ),
            open=True # シートを表示可能にしておく
        )

        # シートを表示する
        page.overlay.append(add_event_btm_sheet)
        page.update()

    def delete_event(event,*,e=None):
        """イベントを削除する.イベントカードのDeleteボタンで作動

        Args:
            event (dict): _description_
            e (flet_core.control_event.ControlEvent, optional): 
            この関数をイベントハンドラとして定義するときに必要. デフォルトはNone(普通の関数として利用するため).
        """        
        # alert_dialogでCancelボタンが押されたときの処理
        def not_delete_event(e):
            alert_dialog.open = False
            page.update()

        # alert_dialogでDeleteボタンが押されたときの処理
        def do_delete_event(e):
            alert_dialog.open = False
            main_page.disabled = True
            page.update()

            # イベントを削除する
            del_msg = sa.delete_event(event)
            if event['id'] in event_cards_column_list:
                # イベントカードを削除
                delete_event_card(event)

            load_days_column()

            main_page.disabled = False
            page.update()

        # 本当に削除するか確認するアラートダイアログ
        alert_dialog = ft.AlertDialog(
            title=ft.Text(f"Delete ' {event['summary']} '?"),
            actions=[
                ft.TextButton("Cancel", on_click=not_delete_event),
                ft.TextButton("Delete", on_click=do_delete_event,style=ft.ButtonStyle(color=ft.colors.RED)),
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

        # アラートダイアログを表示
        page.dialog = alert_dialog
        alert_dialog.open = True
        page.update()
        
    def make_event_card(event):
        """イベントの詳細情報,操作ボタンが乗っているイベントカードを作成する.
        イベントカードの内容：
        イベントのsummary, start, end, descriptionのテキスト
        Doneボタン,イベント変更ボタン,イベント削除ボタン,イベントカード削除ボタン

        Args:
            event (dict): このイベント情報を元にイベントカードを作成する.

        Returns:
            Card: イベントカードが返される.
        """        
        # discriptionが存在しない場合は'No data'を表示する
        discription = 'No data' if not 'description' in event else event['description']

        # タスクが完了状態か未完了状態かによってDoneボタンのテキスト,色を設定する
        if event.get('transparency','opaque') == 'opaque':
            done_btn_msg,done_btn_color = 'Done',PROP_DONE_BTN_COLOR
        else:            
            done_btn_msg,done_btn_color = 'Not yet',PROP_NOTYET_BTN_COLOR

        # Doneボタン作成
        done_btn = make_elevated_button(
            text = done_btn_msg,
            on_click_act = lambda e, event=event:switch_done(event,e=e),
            prop_btn_color = done_btn_color
        )

        # イベントカード作成
        event_card = ft.Card(
            content=ft.Container(
                content = ft.Column(
                    controls=[
                        ft.Text(
                            (
                                f"{event['summary']}\n"
                                f"s:{event['start'].get('dateTime', event['start'].get('date'))[5:16].replace('T',' ')}\n"
                                f"e:{event['end'].get('dateTime', event['end'].get('date'))[5:16].replace('T',' ')}\n"
                                f"{discription}"
                            ),
                            selectable=True
                        ),
                        ft.Row(controls=[
                            done_btn,
                            ft.IconButton(ft.icons.EDIT,on_click=lambda e,event=event:make_edit_event_btm_sheet(event,e=e)),
                            ft.IconButton(ft.icons.DELETE_FOREVER,on_click=lambda e,event=event:delete_event(event,e=e),icon_color=ft.colors.RED),
                            ft.IconButton(ft.icons.CLOSE,on_click=lambda e,event=event:delete_event_card(event,e=e))
                        ])
                    ]
                ),
                padding=10,
                width=280
            )
        )
        return event_card

    def load_days_column(*,e = None):
        """現在時刻以降に始まるイベント情報を取得し,日付ごとにタスクを並べて表示する.
        タスクはイベントカードを作成するボタンとして並べられる.
        ボタンはイベントのsummaryをボタンの名前として表示する.
        また,ボタンはイベントが完了状態か未完了状態かにより色を変化させる.

        Args:
            e (flet_core.control_event.ControlEvent, optional):
            この関数をイベントハンドラとして定義するときに必要. デフォルトはNone(普通の関数として利用するため).
        """        
        # 処理中の表示
        days_column.controls = [ft.ProgressRing()]
        page.update()
        days_column.controls.clear()
        
        events_dict = sa.get_events() # イベントを取得

        if events_dict is None:
            days_column.controls.append(ft.Text("No events"))
        else:
            # イベントが存在する場合
            for date,events_list in events_dict.items():
                day_events_row = ft.Row(wrap=True,width=page.window_width -95)

                # ある一日のイベント達に,それぞれ対応するイベントカードを作成するボタンを作り,一つのrowとしてまとめる
                for event in events_list:
                    event_btn = make_elevated_button(
                        event['summary'],
                        lambda e, event=event:add_event_card(event,e=e),
                        PROP_DONE_BTN_COLOR if event.get('transparency','opaque') == 'opaque' else PROP_NOTYET_BTN_COLOR
                    )
                    day_events_row.controls.append(event_btn)

                # 日付を表すボタン(機能はない)とイベントボタンが並んでいるrowを一つにまとめる
                one_day_row = ft.Row(controls=[
                    ft.ElevatedButton(date[5:],style=ft.ButtonStyle(padding=0)),
                    day_events_row
                    ],
                    vertical_alignment="START"
                )
                # columnに全ての日付分追加
                days_column.controls.append(one_day_row)
        page.update()
    
    def delete_event_card(event,*,e=None):
        """渡されたイベントのイベントカードを削除する.

        Args:
            event (dict): 削除するイベントカードのイベント情報.
            e (flet_core.control_event.ControlEvent, optional):
            この関数をイベントハンドラとして定義するときに必要. デフォルトはNone(普通の関数として利用するため).
        """        
        index = event_cards_column_list.index(event['id'])
        del event_cards_column_list[index]
        del event_cards_column.controls[index]
        page.update()

    def add_event_card(event,*,e=None):
        """渡されたイベントのイベントカードを作成し,表示させる.
        ただし,作成するイベントカードがすでに存在していた場合,そのカードを削除して終了する.

        Args:
            event (dict): 作成するイベントカードのイベント情報.
            e (flet_core.control_event.ControlEvent, optional):
            この関数をイベントハンドラとして定義するときに必要. デフォルトはNone(普通の関数として利用するため).
        """        
        if event['id'] in event_cards_column_list:
            delete_event_card(event)
        else:
            event_cards_column_list.insert(0,event['id'])
            event_cards_column.controls.insert(0,make_event_card(event))

            page.update()

    class DateTimePickerClass:
        # make_edit_event_btm_sheet内で使用するクラス
        # イベントの開始日時と終了日時を決めてもらうときに使用するDatePicker,TimePickerを扱う.
        def __init__(self,init_date,init_time):
            self.date_picker = ft.DatePicker(
                value=init_date,
                confirm_text="Confirm",
                on_change=lambda _: self.set_btn_date()
            )
            page.overlay.append(self.date_picker)
            self.btn_pick_date = ft.OutlinedButton(
                text=f"{self.date_picker.value}"[:10],
                on_click=lambda _: self.date_picker.pick_date()
            )

            self.time_picker = ft.TimePicker(
                value=init_time,
                confirm_text="Confirm",
                error_invalid_text="Time out of range",
                on_change=lambda _: self.set_btn_time()
            )
            page.overlay.append(self.time_picker)
            self.btn_pick_time = ft.OutlinedButton(
                text=f"{self.time_picker.value}"[:5],
                on_click=lambda _: self.time_picker.pick_time()
            )

        # ボタンに表示するテキストを変更する
        def set_btn_date(self):
            self.btn_pick_date.text = f"{self.date_picker.value}"[:10]
            page.update()
        def set_btn_time(self):
            self.btn_pick_time.text = f"{self.time_picker.value}"[:5]
            page.update()

    def make_edit_event_btm_sheet(event,*,e=None):
        """すでに存在するイベントの情報を変更するシートを作成,表示する.

        Args:
            event (dict): 変更するイベントの情報.
            e (flet_core.control_event.ControlEvent, optional):
            この関数をイベントハンドラとして定義するときに必要. デフォルトはNone(普通の関数として利用するため).
        """        
        input_summary = ft.TextField(
                            label="input task name",
                            hint_text="<task name>",
                            value=f"{event['summary']}",
                            autofocus=True
                        )
        
        start_datetime_picker = DateTimePickerClass(event['start'].get('dateTime')[:10],event['start'].get('dateTime')[11:16])
        input_start_datetime = ft.Row(controls=[
                            ft.Text("start :"),
                            start_datetime_picker.btn_pick_date,
                            start_datetime_picker.btn_pick_time
                        ])
        
        end_datetime_picker = DateTimePickerClass(event['end'].get('dateTime')[:10],event['end'].get('dateTime')[11:16])
        input_end_datetime = ft.Row(controls=[
                            ft.Text(" end :"),
                            end_datetime_picker.btn_pick_date,
                            end_datetime_picker.btn_pick_time
                        ])

        input_description = ft.TextField(
                            label="input task memo",
                            hint_text="<memo>",
                            value=f"{event.get('description','')}",
                            multiline=True,
                            min_lines=3,
                            max_lines=5
                        )
        
        edit_event_columun = ft.Column(
            controls=[
                ft.Text("Edit event",size=15,weight=ft.FontWeight.BOLD,color=ft.colors.BLUE_200),
                input_summary,
                input_start_datetime,
                input_end_datetime,
                input_description,
                ft.Row(controls=[
                    ft.IconButton(ft.icons.SEND,icon_color=ft.colors.BLUE_200,tooltip="send",on_click=lambda e,event=event:btn_send_edit_event(event,e=e)),
                    ft.IconButton(ft.icons.CLOSE,on_click=lambda e:close_btm_sheet(e=e))
                ])
            ]
        )

        edit_event_btm_sheet = ft.BottomSheet(
            content = ft.Container(
                content=edit_event_columun,
                padding=15
            ),
            open=True
        )
        
        # シートを閉じる
        def close_btm_sheet(*,e=e):
            edit_event_btm_sheet.open=False
            edit_event_btm_sheet.update()

        # 送信ボタンの処理
        def btn_send_edit_event(event,*,e=None):            
            # 全てのボタン,入力欄を選択不能にする
            main_page.disabled = True
            edit_event_columun.disabled = True
            page.update()
            edit_event_btm_sheet.update()

            # 入力を元にイベント情報を書き換える
            event['summary'] = input_summary.value
            event['description'] = input_description.value
            event['start'] = {'dateTime': f'{str(start_datetime_picker.date_picker.value)[:10]}T{str(start_datetime_picker.time_picker.value)[:5]}:00+09:00'}
            event['end'] = {'dateTime': f'{str(end_datetime_picker.date_picker.value)[:10]}T{str(end_datetime_picker.time_picker.value)[:5]}:00+09:00'}

            # カレンダー上のイベントを変更する
            updated_event = sa.edit_event(event)

            if event['id'] in event_cards_column_list:
                delete_event_card(event)
            add_event_card(event)

            load_days_column()

            main_page.disabled = False
            edit_event_columun.disabled = False
            page.update()
            edit_event_btm_sheet.update()

            close_btm_sheet()

        # シートを表示
        page.overlay.append(edit_event_btm_sheet)
        page.update()

    def switch_done(event,*,e=None):
        """イベントの完了,未完了状態を切り替える.

        Args:
            event (dict): 切り替えるイベントの情報.
            e (flet_core.control_event.ControlEvent, optional):
            この関数をイベントハンドラとして定義するときに必要. デフォルトはNone(普通の関数として利用するため).
        """        
        main_page.disabled = True
        index = event_cards_column_list.index(event['id'])
        event_cards_column.controls[index] = ft.Card(ft.ProgressRing())
        page.update()

        updated_event = sa.switch_done(event) # 切り替え

        load_days_column()
        event_cards_column.controls[index] = make_event_card(updated_event)
        main_page.disabled = False
        page.update()
    # 関数定義ここまで
        
    # ウィンドウの設定
    page.window_width = 320
    page.window_height = 1000
    page.window_left = 1600
    page.window_top = 50
    page.scroll = ft.ScrollMode.HIDDEN
    page.window_title_bar_hidden = True
    page.window_title_bar_buttons_hidden = True

    days_column = ft.Column() # 日付とタスクが並んで表示されるcolumn.

    
    event_cards_column_list = [] # イベントカードのidを保存しておくリスト
    event_cards_column = ft.Column() # イベントカードを並ばせて表示するcolumn

    # ウィンドウに表示する全てのコンテンツをcolumnに入れる.
    main_page = ft.Column(
        controls=[
            ft.Row(controls=[             
                ft.IconButton(ft.icons.CHANGE_CIRCLE,on_click=lambda e:load_days_column(e=e)),
                ft.IconButton(ft.icons.ADD_CARD,icon_color=ft.colors.BLUE_200,tooltip="make event",on_click=make_add_event_btm_sheet),
                ft.WindowDragArea(ft.Container(bgcolor='#252537', padding=18, border_radius=10), expand=True),
                ft.IconButton(ft.icons.CLOSE, on_click=lambda _: page.window_close())
             ]),
            ft.Divider(),
            ft.Container(content=days_column,padding=10),
            ft.Divider(),
            event_cards_column
        ]
    )
    
    page.add(
        main_page
    )

    # 初めにイベントを読み込む
    load_days_column()

ft.app(target=main)
