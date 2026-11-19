# Proxy Django/Gunicorn (M.Ouve) — incluir dentro de <VirtualHost>
# API: /api/v1/*  |  Admin: /admin/

# Evita X-Forwarded-Host do proxy externo (hostname interno) que gera 400 no Django.
RequestHeader unset X-Forwarded-Host
# Origem HTTP para o Gunicorn; o site público é HTTPS.
RequestHeader set X-Forwarded-Proto "https"

Alias /static/ /var/www/ouve/backend/staticfiles/
<Directory /var/www/ouve/backend/staticfiles>
    Require all granted
</Directory>

Alias /media/ /var/www/ouve/backend/media/
<Directory /var/www/ouve/backend/media>
    Require all granted
</Directory>

ProxyPass /static/ !
ProxyPass /media/ !

ProxyTimeout 300

ProxyPass /api/ http://127.0.0.1:8765/api/
ProxyPassReverse /api/ http://127.0.0.1:8765/api/

ProxyPass /admin/ http://127.0.0.1:8765/admin/
ProxyPassReverse /admin/ http://127.0.0.1:8765/admin/
