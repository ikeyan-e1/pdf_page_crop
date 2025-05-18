import TkEasyGUI as eg

def open_sub_window():
    """サブウィンドウを開き、選択結果を返す"""
    layout_sub = [
        [eg.Text("選択してください")],
        [eg.InputText("", key="-x1-", size=(10,30)), eg.InputText("", key="-test_text-", size=(10,30))],
        [eg.Button("OK"), eg.Button("キャンセル")]
    ]
    window = eg.Window("frm_crop", layout=layout_sub, finalize=True)

    # (3) event loop
    while True:
        event, values = window.read()

        if event == "OK":
            window.close()
            return "OKが選択されました"
        elif event in ["キャンセル", eg.WINDOW_CLOSED]:
            window.close()
            return "キャンセルされました"


