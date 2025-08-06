class ProductViewerRouter:
    """
    既存データベースのテーブルを読み取り専用にするルーター
    """
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'product_viewer':
            return 'default'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'product_viewer':
            # ProductViewerアプリのモデルは書き込み禁止
            return None
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'product_viewer':
            # ProductViewerアプリのマイグレーションは実行しない
            return False
        return db == 'default'