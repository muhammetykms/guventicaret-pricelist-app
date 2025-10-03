# Excel Veri Klasörü

Uygulama bu klasördeki Excel dosyalarını **yerel kaynak** olarak kullanır.
Bu dosyalar Git’e gönderilmez (bkz. .gitignore).

Beklenen dosyalar ve sayfa (sheet) adları:

- `Yaglar.xlsx` (sheet: **Yağ**)  
  Sütunlar: `Marka | Urun | Viskozite | Litre | Birim Fiyat (TL) | Satış Fiyat (TL)`

- `Akuler.xlsx` (sheet: **Akü**)  
  Sütunlar: `ÜRÜN | KDV HARİÇ LİSTE FİYATI | 5% (2 ay vade) | 8% (nakit) | HURDA | HRD DÜŞÜLMÜŞ`

- `Filtreler.xlsx` (sheet: **Filtre**)  
  Sütunlar: `Mal Kodu | Mal Adı | Birim Fiyat | Satış Fiyat`

- `Antifriz.xlsx` (sheet: **Antifriz**)  
  Sütunlar: `Marka | Urun | Litre | Birim Fiyat (TL) | Satış Fiyat (TL)`

- `KatkiMaddeleri.xlsx` (sheet: **Katkı**)  
  Sütunlar: `İsim | Birim Fiyat (TL) | Satış Fiyat (TL)`

> Dosyalar bu isimlerle, sayfalar da bu adlarla olmalı.
> “Yedekle” butonu bu dosyaları günceller/oluşturur; Git’e dahil edilmezler.
