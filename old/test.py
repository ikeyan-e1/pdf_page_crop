import fitz  # PyMuPDF

def trim_pdf(input_pdf, output_pdf, page_num, rect):
    """
    PDFの指定ページを指定したサイズにトリミングする。

    :param input_pdf: 入力PDFファイルのパス
    :param output_pdf: 出力PDFファイルのパス
    :param page_num: トリミングするページ番号（1から始まる）
    :param rect: トリミングする領域 (x0, y0, x1, y1)
    """
    doc = fitz.open(input_pdf)
    page = doc[page_num - 1]  # ページは0から始まるため調整
    page.set_cropbox(fitz.Rect(rect))  # トリミング領域を設定
    doc.save(output_pdf)
    doc.close()

# 使用例
#input_pdf_path = "example.pdf"
#output_pdf_path = "trimmed_example.pdf"
#page_number = 1  # 1ページ目をトリミング
#crop_rect = (50, 50, 500, 700)  # x0, y0, x1, y1 の座標

#trim_pdf(input_pdf_path, output_pdf_path, page_number, crop_rect)

# mmをポイントに変換する関数（1 mm = 2.83465 pt）
def mm_to_pt(mm):
    return mm * 2.83465

def trim_pdf_mm(input_pdf, output_pdf, page_num, x0_mm, y0_mm, width_mm, height_mm):
    """
    PDFページをmm単位で指定してトリミングする。

    :param input_pdf: 入力PDFファイルのパス
    :param output_pdf: 出力PDFファイルのパス
    :param page_num: トリミングするページ番号（1から始まる）
    :param x0_mm: 左上のX座標（mm）
    :param y0_mm: 左上のY座標（mm）
    :param width_mm: トリミング領域の幅（mm）
    :param height_mm: トリミング領域の高さ（mm）
    """
    doc = fitz.open(input_pdf)
    page = doc[page_num - 1]

    # mm単位からポイントへ変換
    x0_pt = mm_to_pt(x0_mm)
    y0_pt = mm_to_pt(y0_mm)
    x1_pt = x0_pt + mm_to_pt(width_mm)
    y1_pt = y0_pt + mm_to_pt(height_mm)

    # トリミング領域を設定
    page.set_cropbox(fitz.Rect(x0_pt, y0_pt, x1_pt, y1_pt))

    # 保存
    doc.save(output_pdf)
    doc.close()

# 使用例（A3のPDFをA4サイズへトリミング）
input_pdf_path = "example.pdf"
output_pdf_path = "example_a5_trimmed.pdf"
page_number = 1

# A3 -> A4 のトリミング座標（左上のX, Yと幅・高さ）
x0_mm, y0_mm = 0, 0  # 左上（原点）
width_mm, height_mm = 210, 297  # A4サイズ（mm）

trim_pdf_mm(input_pdf_path, output_pdf_path, page_number, x0_mm, y0_mm, width_mm, height_mm)
print("PDFのページをmm単位でトリミングしました！")

