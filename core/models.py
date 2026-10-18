from django.db import models


class BaseModel(models.Model):
    """
    Tüm modellerin türeyeceği soyut (abstract) temel model.
    - created_at / updated_at: zaman damgaları
    - is_deleted: soft delete için (fiziksel silme yerine işaretleme)
    """
    created_at = models.DateTimeField(auto_now_add=True)   # oluşturulunca 1 kez
    updated_at = models.DateTimeField(auto_now=True)       # her save'de güncellenir
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True          # kendi başına tablo OLUŞTURMAZ, miras alınır
        ordering = ['-created_at']  # en yeniler önce