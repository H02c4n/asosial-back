#!/bin/sh
set -e

echo "⏳ Veritabanı bekleniyor..."
while ! python -c "import psycopg2; psycopg2.connect(
    dbname='${DB_NAME:-asosial}',
    user='${DB_USER:-asosial}',
    password='${DB_PASSWORD:-asosial}',
    host='${DB_HOST:-postgres}',
    port='${DB_PORT:-5432}'
)" 2>/dev/null; do
  sleep 1
done
echo "✅ Veritabanı hazır"

echo "🔄 Migration'lar uygulanıyor..."
python manage.py migrate --noinput

echo "📦 Static dosyalar toplanıyor..."
python manage.py collectstatic --noinput || true

echo "👤 Superuser kontrol ediliyor..."
python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ admin oluşturuldu (şifre: admin123)')
else:
    print('ℹ️ admin zaten var')
" || true

echo "🚀 Sunucu başlatılıyor: $@"
exec "$@"