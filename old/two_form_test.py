import sys
import fitz  # PyMuPDF
import TkEasyGUI as eg
from PIL import Image, ImageTk
from two_form2_test import open_sub_window  # サブウィンドウの関数をインポート

def main():
    #
    pdf_document = None

    # メニュー定義
    menu_def = [
        ['File',['!New', '---', 'Open', 'Save', 'Exit']],
        ['Edit',['!Paste','Redo','Undo']],
    ]

    # 画面1レイアウトの定義

    # (1) create Element

    layout = [
        [eg.Menu(menu_def)],
        [eg.Label("x1,y1:"), eg.InputText("", key="-x1-", size=(10,30)), eg.InputText("", key="-y1-", size=(10,30)),],
        [eg.Label("x2,y2:"), eg.InputText("", key="-x2-", size=(10,30)), eg.InputText("", key="-y2-", size=(10,30)),],
        [eg.Button("適用", size=(10,1), key="-app-"),],
        [eg.Label("                                 "), eg.Button("終了", size=(10,1), key="Exit")]
    ]

    window = eg.Window("Canvas", layout=layout, finalize=True)




    # (3) event loop
    while True:
        event, values = window.read()

        # 左上のバツボタンでウィンドウを閉じる
        if event in ["Exit", eg.WINDOW_CLOSED]:
            print("プログラムの終了ボタンが押されました。")
            if pdf_document is not None:
                pdf_document.close()
            window.close()
            break

        if event == "Open":
            result = open_sub_window()  # サブウィンドウを開いて結果を取得
            print(result)




if __name__ == '__main__':
    main()



