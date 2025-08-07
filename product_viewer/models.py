from django.db import models

class ProductPhoto(models.Model):
    """
    既存データベースのT_製品写真サブテーブルとマッピングするモデル
    """
    product_photo_code = models.CharField(
        max_length=15,
        primary_key=True,
        db_column='製品写真コード',
        verbose_name='製品写真コード'
    )
    product_code = models.CharField(
        max_length=10,
        db_column='製品コード',
        verbose_name='製品コード'
    )
    hno = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        db_column='HNO',
        verbose_name='番号',
        null=True,
        blank=True
    )
    path = models.CharField(
        max_length=255,
        db_column='PATH',
        verbose_name='画像パス'
    )
    remarks = models.CharField(
        max_length=255,
        db_column='備考',
        verbose_name='備考',
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'T_製品写真サブ'
        managed = False  # 既存テーブルなのでDjangoでは管理しない
        verbose_name = '製品写真'
        verbose_name_plural = '製品写真'
        ordering = ['product_code', 'hno']

    def __str__(self):
        return f"{self.product_code} - {self.product_photo_code}"
