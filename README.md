# pdf_page_crop

PDFファイルの指定したページのトリミングをGUIで行うツールです。  
厳密には、表示される範囲を絞るといった処理になっており、データサイズが減ることはありません。  
  
【経緯】  
A4サイズで製本されたもの（契約書など）をコピー機でスキャンする際に、  
良い感じに片側のページだけをスキャンするのがあまり得意で無かったので  
いっそ、A3で両方のページをスキャンして、あとからA4の範囲で切り出したいと思ったのですが、  
それが実現できるツールが大体有料のアプリだったので、その部分だけ別アプリとして作成した次第です。  
  


# EXE化する場合
  
Python3.13環境では、上手くいきませんでした。  
Python3.10を準備し、`requirements_py310.txt`にあるライブラリをインストールする。  
その後、下記のコマンドでコンパイルできました。  
```
Nuitka --standalone --onefile --enable-plugins=tk-inter pdf_edit_main.py
```
  
  
どうやら、PyMuPDFのバージョンが新しいとヒープメモリが足りなくなってコンパイル中に落ちるようです。
うちの環境が、32GBだったので、もっと多くのメモリを詰んでいる環境であれば通るかもしれません。



※Portable Python使用時  
```
python <Portable Pythonインストール先>\App\Python\Lib\site-packages\nuitka\__main__.py --standalone --onefile --enable-plugins=numpy --enable-plugins=tk-inter module1.py
```
```
Nuitka --standalone --onefile --enable-plugins=tk-inter pdf_edit_main.py
```