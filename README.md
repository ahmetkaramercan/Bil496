# BIL496
## Bitirme Projesi

### ETÜHEALTH

**Yazarlar:**
  - Kerem Yalçınkaya
  - Ahmet Karamercan
  
**Dosya Açıklamaları:**
  - `model_train`: Fine-Tune DiaBert Modelinin eğitimine ait dosyaları içerir. `Model_train_2.ipynb` dosyası, drive linkinde bulunan modelin son halini oluşturan dosyadır.
  - `model`: Eğitilmiş modele ait dosyaları içeren klasördür. Drive linkinde bulunan model bu dosyaya koyulmalıdır.
  - `instance`: Database'i içeren dosyadır. İçindeki db uzantılı dosya silinerek yeni bir database oluşturulabilir.
  - `bitirme`: Backend dosyalarını, templates klasörünü, static klasörünü içerir.
    - `bitirme/templates`: Frontend dosyalarını içerir.
    - `bitirme/static`: Projedeki fotoğraflar gibi statik dosyaları tutar.

**Fine-Tuned DiaBert Model:**
[Drive Link](https://drive.google.com/drive/folders/1TVATi7F5xFPo0ArAgDRkBsT5Wa0cJiTQ?usp=drive_link)

**Notlar:**
- Drive dosyasındaki eğitilmiş Fine-Tuned DiaBert Modeli indirilerek `model` klasörünün içerisine konulmalıdır.
- Terminal üzerinden BİL496 klasörüne girildikten sonra `main.py` dosyası çalıştırılarak uygulama çalıştırılır.
- `instance` dosyası içersindeki db uzantılı dosya silinip uygulama tekrar çalıştırılarak database sıfırlanabilir.

