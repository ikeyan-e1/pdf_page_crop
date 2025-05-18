import sys
import fitz  # PyMuPDF
import TkEasyGUI as eg
from PIL import Image, ImageTk

def render_pdf_page(pdf_doc, page_num):
    """PDFを画像に変換"""
    page = pdf_doc[page_num]
    pix = page.get_pixmap()
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    max_size = (400,400) # 画面のキャンバスのサイズと同じにする。
    img.thumbnail(max_size) # キャンバスに収まるように縦横比を維持して縮小
    return img

def on_mouse_down(event, canvas):
    """ドラッグ開始の座標を記録"""
    print("マウスが押された")
    canvas.start_x = event.x
    canvas.start_y = event.y
    canvas.create_rectangle(canvas.start_x, canvas.start_y, canvas.start_x, canvas.start_y, outline="red", tag="selection_rectangle")

def on_mouse_drag(event, canvas):
    """範囲選択のために矩形を描画"""
    print("範囲選択")
    canvas.delete("selection_rectangle")
    canvas.create_rectangle(canvas.start_x, canvas.start_y, event.x, event.y, outline="red", tag="selection_rectangle")

def on_mouse_up(event, canvas):
    """ドラッグ終了時の範囲を記録"""
    x1, y1, x2, y2 = canvas.coords("selection_rectangle")
    #canvas.delete("selection_rectangle")
    print(f"選択された範囲: ({x1}, {y1}) - ({x2}, {y2})")

def display_rect_coord(wnd,canvas):
    x1, y1, x2, y2 = canvas.coords("selection_rectangle")
    #wnd['-x1-'].value = x1
    #wnd['-y1-'].value = y1
    #wnd['-x2-'].value = x2
    #wnd['-y2-'].value = y2
    wnd['-x1-'].set_text(x1)
    wnd['-y1-'].set_text(y1)
    wnd['-x2-'].set_text(x2)
    wnd['-y2-'].set_text(y2)



def copy_pdf_page(pdf_doc, copy_page_num, insert_page_num):
    '''
    pdf_doc         as pdf object # PDFオブジェクト
    copy_page_num   as int        # 複製するページ番号
    insert_page_num as int        # 挿入するページ番号（挿入後のページ番号）
    '''

    pdf_doc.insert_pdf(pdf_doc, from_page=copy_page_num, to_page=copy_page_num, start_at=insert_page_num)

    return pdf_doc


def main():
    #
    pdf_document = None
    # ListBoxの値
    image_file_list = []

    # メニュー定義
    menu_def = [
        ['File',['!New', '---', 'Open', 'Save', 'Exit']],
        ['Edit',['!Paste','Redo','Undo']],
    ]

    # 画面レイアウトの定義

    # (1) create Element
    canvas = eg.Canvas(size=(400, 400),
                key="-canvas-",
                background_color="gray",
                enable_events=True)

    layout = [
        [eg.Menu(menu_def)],
        [
            eg.Listbox(values=image_file_list, key="-page_list-", size=(10,25), enable_events=True), # 50文字,30行
            canvas,
        ],
        [eg.Label("x1,y1:"), eg.InputText("", key="-x1-", size=(10,30), enable_focus_events=True), eg.InputText("", key="-y1-", size=(10,30)),],
        [eg.Label("x2,y2:"), eg.InputText("", key="-x2-", size=(10,30)), eg.InputText("", key="-y2-", size=(10,30)),],
        [eg.Button("適用", size=(10,1), key="-app-"),],
        [eg.Label("                                 "), eg.Button("終了", size=(10,1), key="Exit")]
    ]

    window = eg.Window("Canvas", layout=layout, finalize=True)

    # (2) bind custom events
    # マウス操作のバインド
    canvas.bind("<ButtonPress>", "press")
    canvas.bind("<ButtonRelease>", "release")
    canvas.bind("<Motion>", "motion")


    # (3) event loop
    while True:
        event, values = window.read()
        frm_canvas = window["-canvas-"]
        if event in ["-x1-","-y1"]:
            if values.get('event_type')=='focusout':
                print('x1からフォーカスがロストしました。')
            print(event)
            print(values)

        # 左上のバツボタンでウィンドウを閉じる
        if event in ["Exit", eg.WINDOW_CLOSED]:
            print("プログラムの終了ボタンが押されました。")
            if pdf_document is not None:
                pdf_document.close()
            window.close()
            break

        # メニュー操作時の処理
        if event =="Save":
            # 保存ボタン押下時の処理
            if len(image_file_list) == 0:
                continue

            # file types
            file_types = (("PDF files", "*.pdf"),)
            output_path = eg.popup_get_file("", file_types=file_types, save_as=True)
            if len(output_path) == 0:
                continue
            #create_multipage_tiff(image_file_list, output_path, quality=75, compression=COMPRESSION_DICT[values["-compression-"]])
            eg.print(f"マルチページTiffを {output_path} に保存しました。")

        if event == "Open":
            # ファイル追加ボタン押下時の動作
            # file types
            file_types = (
                ("PDF files", "*.pdf;"),
                ("All files", "*.*"),
            )
            # popup
            files = eg.popup_get_file(
                "Please select PDF File.",
                file_types=file_types,
                multiple_files=False,
            )
            #print(files)
            pdf_document = fitz.open(files)
            image_file_list = [ a for a in range(0,pdf_document.page_count)]
            window.get_element_by_key('-page_list-').update(values=image_file_list)

        if event == "-page_list-":
            # ファイルリストを選択したときの動作

            # 画像プレビュー画面に選択された画像を表示する。
            page_num = int(values["-page_list-"][0])
            img = render_pdf_page(pdf_document,page_num)
            if len(files) > 0:
                tk_img = ImageTk.PhotoImage(img)
                frm_canvas.create_image(0, 0, image=tk_img, anchor="nw")


        if event == "-canvas-press":
            #print(values["event"])
            #print(values)
            #print(values["event"].num) # 1:左ボタン 2:中ボタン 3:右ボタン
            if values["event"].num == 1:
                on_mouse_down(values["event"], frm_canvas)


        if event == "-canvas-release":
            if values["event"].num == 1:
                on_mouse_up(values["event"], frm_canvas)
                display_rect_coord(window, frm_canvas)

        if event == "-canvas-motion":
            if values["event"].state == 264:
                on_mouse_drag(values["event"], frm_canvas)



if __name__ == '__main__':
    main()



