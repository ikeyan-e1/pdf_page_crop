# MainWindowに関する処理を書いて行く。
import os
import sys
import fitz  # PyMuPDF
import TkEasyGUI as eg
from PIL import Image, ImageTk
from pdf_edit_crop import frm_crop  # ページのトリミングフ用ォーム

def render_pdf_page(pdf_doc, page_num):
    """PDFを画像に変換"""
    page = pdf_doc[page_num]
    pix = page.get_pixmap()
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    max_size = (400,400) # 画面のキャンバスのサイズと同じにする。
    img.thumbnail(max_size) # キャンバスに収まるように縦横比を維持して縮小
    return img

def copy_pdf_page(pdf_doc, pdf_doc2, copy_page_num, insert_page_num):
    '''
    pdf_doc         as pdf object # PDFオブジェクト
    copy_page_num   as int        # 複製するページ番号
    insert_page_num as int        # 挿入するページ番号（挿入後のページ番号）
    '''

    pdf_doc.insert_pdf(pdf_doc2, from_page=copy_page_num, to_page=copy_page_num, start_at=insert_page_num)

    return pdf_doc




def main():
    #
    pdf_document = None
    # ListBoxの値
    image_file_list = []

    # メニュー定義
    menu_def = [
        ['File',['Open', 'Save', 'Exit']],
        ['Edit',['PageCopy','CropPage','!Redo','!Undo']],
    ]

    # 画面レイアウトの定義

    # create Element
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
        [eg.Button("適用", size=(10,1), key="-app-"),],
        [eg.Label("                                 "), eg.Button("終了", size=(10,1), key="Exit")]
    ]

    window = eg.Window("Canvas", layout=layout, finalize=True)

    # event loop
    while True:
        event, values = window.read()
        frm_canvas = window["-canvas-"]

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
            pdf_document.save(output_path)
            eg.print(f"PDFを {output_path} に保存しました。")

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


        if event == "PageCopy":
            # ページの複製(PageCopy)が選択された場合
            if pdf_document is None:
                continue

            page_num = int(values["-page_list-"][0])
            #pdf_document2 = fitz.open(files)
            pdf_document.save('./tmp.pdf')                                                     # 今のPDFを一時保存
            pdf_document2 = fitz.open('./tmp.pdf')                                             # 保存したPDFを別のDocumentとして開く。
            pdf_document = copy_pdf_page(pdf_document, pdf_document2, page_num , page_num + 1) # ページの複製
            pdf_document2.close()                                                              # 一時PDFを閉じる。
            os.remove('./tmp.pdf')                                                             # 一時ファイルの削除
            # ページ一覧の再作成
            image_file_list = [ a for a in range(0,pdf_document.page_count)]
            window.get_element_by_key('-page_list-').update(values=image_file_list)
            continue

        if event == "CropPage":
            # ページのトリミング(CropPage)が選択された場合
            if pdf_document is None:
                continue

            page_num = int(values["-page_list-"][0])
            result = frm_crop(pdf_document, page_num )  # サブウィンドウを開いて結果を取得
            print(result)
            pdf_document = result
            image_file_list = [ a for a in range(0,pdf_document.page_count)]
            window.get_element_by_key('-page_list-').update(values=image_file_list)

            print(result)

        # Main Windowのイベント
        if event == "-page_list-":
            # ファイルリストを選択したときの動作

            # 画像プレビュー画面に選択された画像を表示する。
            try:
                page_num = int(values["-page_list-"][0])
            except IndexError:
                # リストボックスで上手く選択できてないときに来る予定
                continue
            img = render_pdf_page(pdf_document,page_num)
            if len(files) > 0:
                tk_img = ImageTk.PhotoImage(img)
                frm_canvas.create_image(0, 0, image=tk_img, anchor="nw")




if __name__ == '__main__':
    main()



