import sys
import fitz  # PyMuPDF
import re
import TkEasyGUI as eg
from PIL import Image, ImageTk

PREVIEW_CANVAS_SIZE = (400,400) # PDFプレビュー画面のサイズ

def render_pdf_page(pdf_doc, page_num, preview_canvas_size):
    """PDFを画像に変換"""
    page = pdf_doc[page_num]
    pix = page.get_pixmap()
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    max_size = preview_canvas_size # 画面のキャンバスのサイズと同じにする。
    img.thumbnail(max_size) # キャンバスに収まるように縦横比を維持して縮小
    #print((pix.width, pix.height))
    #print(img.size) # (横pix,縦pix )
    resize_rate = img.size[0] / pix.width
    return img, resize_rate

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

def display_rect_coord(wnd,canvas,resize_rate=1):
    x1, y1, x2, y2 = canvas.coords("selection_rectangle")
    #wnd['-x1-'].value = x1
    #wnd['-y1-'].value = y1
    #wnd['-x2-'].value = x2
    #wnd['-y2-'].value = y2
    wnd['-left-'].set_text(pt_to_mm(x1 * (1/resize_rate))) # x1
    wnd['-top-'].set_text(pt_to_mm(y1 * (1/resize_rate))) # y1
    wnd['-width-'].set_text(pt_to_mm((x2-x1) * (1/resize_rate))) # x2 - x1
    wnd['-height-'].set_text(pt_to_mm((y2-y1) * (1/resize_rate))) # y2 - y1

# mmをポイントに変換する関数（1 mm = 2.83465 pt）
def mm_to_pt(mm):
    return mm * 2.83465

# ポイントをmmに変換する関数（1 mm = 2.83465 pt）
def pt_to_mm(pt):
    return pt / 2.83465

def is_valid_number(value):
    """正規表現を使って数値（整数・小数）をチェック"""
    pattern = r"^-?\d+(\.\d+)?$"  # 負の数も許容
    return bool(re.match(pattern, value))

def extract_valid_numbers(text):
    """入力された文字列から数値（整数・小数）を抽出"""
    pattern = r"-?\d+(\.\d+)?"
    match = re.search(pattern, text)
    #print(match.group() if match else "なし")  # 入力："abc 123 def -45.67 ghi" 出力: '123'
    #print(re.findall(pattern, text))         # 入力："abc 123 def -45.67 ghi" 出力: ['123','-45.67']

    return match.group() if match else "0"


def trim_pdf_mm(pdf_doc, page_num, x0_mm, y0_mm, width_mm, height_mm):
    """
    PDFページをmm単位で指定してトリミングする。

    :param pdf_doc: PyMuPDF PDF_Document Object
    :param page_num: トリミングするページ番号（1から始まる）
    :param x0_mm: 左上のX座標（mm）
    :param y0_mm: 左上のY座標（mm）
    :param width_mm: トリミング領域の幅（mm）
    :param height_mm: トリミング領域の高さ（mm）
    """

    page = pdf_doc[page_num - 1]

    # mm単位からポイントへ変換
    x0_pt = mm_to_pt(x0_mm)
    y0_pt = mm_to_pt(y0_mm)
    x1_pt = x0_pt + mm_to_pt(width_mm)
    y1_pt = y0_pt + mm_to_pt(height_mm)

    # トリミング領域を設定
    page.set_cropbox(fitz.Rect(x0_pt, y0_pt, x1_pt, y1_pt))

    return pdf_doc


def frm_crop(pdf_document, page_num):
    """サブウィンドウを開き、選択結果を返す"""
    # create Element
    canvas = eg.Canvas(size=PREVIEW_CANVAS_SIZE,
                key="-canvas-",
                background_color="gray",
                enable_events=True)

    layout_sub = [
        [
            canvas
        ],
        [eg.Label("左位置(mm):"), eg.InputText("0", key="-left-", size=(10,30), enable_focus_events=True, enable_events=True),
         eg.Label("上位置(mm):"), eg.InputText("0", key="-top-", size=(10,30), enable_focus_events=True, enable_events=True),],
        [eg.Label("　幅　(mm):"), eg.InputText("0", key="-width-", size=(10,30), enable_focus_events=True, enable_events=True),
         eg.Label("高　さ(mm):"), eg.InputText("0", key="-height-", size=(10,30), enable_focus_events=True, enable_events=True),],
        [eg.Button("適用", size=(10,1), key="-app-"),],
        [eg.Button("OK"), eg.Button("キャンセル")]
    ]
    window = eg.Window("frm_crop", layout=layout_sub, finalize=True)

    # (2) bind custom events
    # マウス操作のバインド
    canvas.bind("<ButtonPress>", "press")
    canvas.bind("<ButtonRelease>", "release")
    canvas.bind("<Motion>", "motion")

    frm_canvas = window["-canvas-"]

    # 画像プレビュー画面に選択された画像を表示する。
    img, resize_rate = render_pdf_page(pdf_document, page_num, PREVIEW_CANVAS_SIZE)
    print(resize_rate)
    tk_img = ImageTk.PhotoImage(img)
    frm_canvas.create_image(0, 0, image=tk_img, anchor="nw")

    # (3) event loop
    while True:
        event, values = window.read()

        if event == "OK":
            window.close()
            return "OKが選択されました"
        elif event in ["キャンセル", eg.WINDOW_CLOSED]:
            window.close()
            return "キャンセルされました"

        # 適用ボタン押下時の処理
        if event == "-app-":
            x0_mm = float(extract_valid_numbers(window['-left-'].get()))
            y0_mm = float(extract_valid_numbers(window['-top-'].get()))
            width_mm = float(extract_valid_numbers(window['-width-'].get()))
            height_mm = float(extract_valid_numbers(window['-height-'].get()))
            print(page_num)
            pdf_doc = trim_pdf_mm(pdf_document, page_num + 1, x0_mm, y0_mm, width_mm, height_mm)

            window.close()
            return pdf_doc


        # テキストボックス直接入力時の処理
        if event in ["-left-","-top-","-width-","-height-"]:
            if values.get('event_type')=='change':
                if values.get('event')[0]=='PY_VAR0': # -left-
                    if is_valid_number(window['-left-'].get())==False:
                        window['-left-'].set_text(extract_valid_numbers(window['-left-'].get()))
                if values.get('event')[0]=='PY_VAR1': # -top-
                    if is_valid_number(window['-top-'].get())==False:
                        window['-top-'].set_text(extract_valid_numbers(window['-top-'].get()))
                if values.get('event')[0]=='PY_VAR2': # -width-
                    if is_valid_number(window['-width-'].get())==False:
                        window['-width-'].set_text(extract_valid_numbers(window['-width-'].get()))
                if values.get('event')[0]=='PY_VAR3': # -height-
                    if is_valid_number(window['-height-'].get())==False:
                        window['-height-'].set_text(extract_valid_numbers(window['-height-'].get()))
                print(values)

            if values.get('event_type')=='focusout':
                print("フォーカスが外れました。")
                frm_canvas.delete("selection_rectangle")
                x1 = mm_to_pt(float(window['-left-'].get()) * resize_rate)
                y1 = mm_to_pt(float(window['-top-'].get()) * resize_rate)
                w1 = mm_to_pt(float(window['-width-'].get()) * resize_rate)
                h1 = mm_to_pt(float(window['-height-'].get()) * resize_rate)
                x2 = x1 + w1
                y2 = y1 + h1
                frm_canvas.create_rectangle(x1, y1, x2, y2, outline="red", tag="selection_rectangle")

        # キャンバスの描画系処理
        if event == "-canvas-press":
            #print(values["event"])
            #print(values)
            #print(values["event"].num) # 1:左ボタン 2:中ボタン 3:右ボタン
            if values["event"].num == 1:
                on_mouse_down(values["event"], frm_canvas)

        if event == "-canvas-release":
            if values["event"].num == 1:
                on_mouse_up(values["event"], frm_canvas)
                display_rect_coord(window, frm_canvas, resize_rate)

        if event == "-canvas-motion":
            if values["event"].state == 264:
                on_mouse_drag(values["event"], frm_canvas)

