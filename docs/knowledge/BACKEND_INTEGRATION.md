# Integração com Backend Django

Este documento guia a equipe de backend na implementação da API Django que suportará o **M.Ouve**.

## 📋 Stack Recomendada

```python
# requirements.txt
Django>=5.0
djangorestframework>=3.14
djangorestframework-simplejwt>=5.3
django-cors-headers>=4.3
psycopg2-binary>=2.9  # PostgreSQL
celery>=5.3  # Tarefas assíncronas
redis>=5.0  # Cache e message broker
```

### Extensões PostgreSQL

```sql
CREATE EXTENSION IF NOT EXISTS postgis;  -- Dados geoespaciais
CREATE EXTENSION IF NOT EXISTS vector;   -- pgvector para embeddings
```

## 🗂️ Estrutura Django Sugerida

```
backend/
├── config/                 # Configurações Django
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
│
├── apps/
│   ├── authentication/    # Autenticação (Gov.br, SSO, Padrão)
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   │
│   ├── protocolos/        # Gestão de Protocolos
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── filters.py
│   │   └── urls.py
│   │
│   ├── zeladoria/         # Zeladoria Urbana + IA
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── assistente.py  # Lógica IA/NLP
│   │   └── urls.py
│   │
│   ├── ouvidoria/         # Ouvidoria Institucional
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   │
│   └── notificacoes/      # Sistema de Notificações
│       ├── models.py
│       ├── tasks.py       # Celery tasks
│       └── urls.py
│
├── core/                  # Utilitários compartilhados
│   ├── permissions.py
│   ├── pagination.py
│   └── exceptions.py
│
└── manage.py
```

## 🔐 Implementação de Autenticação

### Models

```python
# apps/authentication/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class Usuario(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    cpf = models.CharField(max_length=14, unique=True)
    telefone = models.CharField(max_length=15, blank=True)
    metodo_autenticacao = models.CharField(
        max_length=20,
        choices=[
            ('govbr', 'Gov.br'),
            ('sso_municipal', 'SSO Municipal'),
            ('padrao', 'Padrão')
        ]
    )
    govbr_sub = models.CharField(max_length=255, blank=True, null=True)
    
    # Campos de auditoria
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'cpf'
    REQUIRED_FIELDS = ['email', 'first_name']

    def __str__(self):
        return f"{self.get_full_name()} ({self.cpf})"
```

### Serializers

```python
# apps/authentication/serializers.py
from rest_framework import serializers
from .models import Usuario

class UsuarioSerializer(serializers.ModelSerializer):
    nome = serializers.SerializerMethodField()
    
    class Meta:
        model = Usuario
        fields = ['id', 'cpf', 'nome', 'email', 'telefone']
    
    def get_nome(self, obj):
        return obj.get_full_name()

class LoginResponseSerializer(serializers.Serializer):
    user = UsuarioSerializer()
    token = serializers.CharField()
    refresh_token = serializers.CharField()
```

### Views

```python
# apps/authentication/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

@api_view(['POST'])
@permission_classes([AllowAny])
def login_padrao(request):
    cpf = request.data.get('cpf')
    senha = request.data.get('senha')
    
    # Validar CPF e senha
    usuario = authenticate_usuario(cpf, senha)
    
    if not usuario:
        return Response(
            {'error': 'Credenciais inválidas'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Gerar tokens JWT
    refresh = RefreshToken.for_user(usuario)
    
    return Response({
        'user': UsuarioSerializer(usuario).data,
        'token': str(refresh.access_token),
        'refresh_token': str(refresh)
    })
```

## 📝 Implementação de Protocolos

### Models

```python
# apps/protocolos/models.py
from django.contrib.gis.db import models as gis_models
from django.db import models
import uuid

class Protocolo(models.Model):
    TIPO_CHOICES = [
        ('ouvidoria', 'Ouvidoria'),
        ('zeladoria', 'Zeladoria')
    ]
    
    STATUS_CHOICES = [
        ('em_analise', 'Em Análise'),
        ('em_andamento', 'Em Andamento'),
        ('resolvido', 'Resolvido'),
        ('rejeitado', 'Rejeitado')
    ]
    
    id = models.CharField(max_length=20, primary_key=True)  # PROT-2024-001
    usuario = models.ForeignKey('authentication.Usuario', on_delete=models.PROTECT)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    categoria = models.ForeignKey('Categoria', on_delete=models.PROTECT)
    descricao = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='em_analise')
    
    # Campos geoespaciais (zeladoria)
    endereco = models.CharField(max_length=255, blank=True)
    localizacao = gis_models.PointField(null=True, blank=True, srid=4326)
    
    # Relacionamentos
    equipe = models.ForeignKey('Equipe', null=True, blank=True, on_delete=models.SET_NULL)
    
    # Metadados
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    # Vetorização para RAG
    embedding = models.VectorField(dimensions=1536, null=True, blank=True)
    
    class Meta:
        ordering = ['-criado_em']
        indexes = [
            models.Index(fields=['usuario', 'status']),
            models.Index(fields=['tipo', 'categoria']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.id:
            # Gerar ID sequencial
            ultimo = Protocolo.objects.order_by('-id').first()
            if ultimo:
                numero = int(ultimo.id.split('-')[-1]) + 1
            else:
                numero = 1
            self.id = f"PROT-2024-{str(numero).zfill(3)}"
        super().save(*args, **kwargs)


class HistoricoProtocolo(models.Model):
    protocolo = models.ForeignKey(Protocolo, related_name='historico', on_delete=models.CASCADE)
    status = models.CharField(max_length=20)
    descricao = models.TextField()
    usuario = models.ForeignKey('authentication.Usuario', on_delete=models.SET_NULL, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)


class AnexoProtocolo(models.Model):
    protocolo = models.ForeignKey(Protocolo, related_name='anexos', on_delete=models.CASCADE)
    arquivo = models.FileField(upload_to='protocolos/%Y/%m/')
    tipo = models.CharField(max_length=50)  # image/jpeg, audio/webm
    criado_em = models.DateTimeField(auto_now_add=True)
```

### Serializers

```python
# apps/protocolos/serializers.py
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import Protocolo, HistoricoProtocolo, AnexoProtocolo

class AnexoSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = AnexoProtocolo
        fields = ['id', 'url', 'tipo', 'criado_em']
    
    def get_url(self, obj):
        return self.context['request'].build_absolute_uri(obj.arquivo.url)


class ProtocoloListSerializer(serializers.ModelSerializer):
    localizacao = serializers.SerializerMethodField()
    anexos = AnexoSerializer(many=True, read_only=True)
    
    class Meta:
        model = Protocolo
        fields = [
            'id', 'tipo', 'categoria', 'descricao', 'status',
            'data_criacao', 'data_atualizacao', 'localizacao', 'anexos'
        ]
    
    def get_localizacao(self, obj):
        if obj.localizacao:
            return {
                'endereco': obj.endereco,
                'latitude': obj.localizacao.y,
                'longitude': obj.localizacao.x
            }
        return None


class ProtocoloDetailSerializer(ProtocoloListSerializer):
    historico = serializers.SerializerMethodField()
    equipe = serializers.SerializerMethodField()
    
    class Meta(ProtocoloListSerializer.Meta):
        fields = ProtocoloListSerializer.Meta.fields + ['historico', 'equipe']
    
    def get_historico(self, obj):
        return [{
            'data': h.criado_em.isoformat(),
            'status': h.status,
            'descricao': h.descricao
        } for h in obj.historico.all()]
    
    def get_equipe(self, obj):
        if obj.equipe:
            return {'id': obj.equipe.id, 'nome': obj.equipe.nome}
        return None


class CriarProtocoloSerializer(serializers.ModelSerializer):
    fotos = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False
    )
    audio = serializers.FileField(write_only=True, required=False)
    latitude = serializers.FloatField(write_only=True, required=False)
    longitude = serializers.FloatField(write_only=True, required=False)
    
    class Meta:
        model = Protocolo
        fields = [
            'tipo', 'categoria', 'descricao', 'endereco',
            'latitude', 'longitude', 'fotos', 'audio'
        ]
    
    def create(self, validated_data):
        fotos = validated_data.pop('fotos', [])
        audio = validated_data.pop('audio', None)
        latitude = validated_data.pop('latitude', None)
        longitude = validated_data.pop('longitude', None)
        
        # Criar ponto geográfico
        if latitude and longitude:
            from django.contrib.gis.geos import Point
            validated_data['localizacao'] = Point(longitude, latitude, srid=4326)
        
        # Associar usuário
        validated_data['usuario'] = self.context['request'].user
        
        protocolo = Protocolo.objects.create(**validated_data)
        
        # Processar anexos
        for foto in fotos:
            AnexoProtocolo.objects.create(
                protocolo=protocolo,
                arquivo=foto,
                tipo=foto.content_type
            )
        
        if audio:
            AnexoProtocolo.objects.create(
                protocolo=protocolo,
                arquivo=audio,
                tipo=audio.content_type
            )
        
        # Criar histórico inicial
        HistoricoProtocolo.objects.create(
            protocolo=protocolo,
            status='em_analise',
            descricao='Protocolo criado'
        )
        
        # Disparar tarefa assíncrona para análise IA
        from apps.zeladoria.tasks import analisar_protocolo_ia
        analisar_protocolo_ia.delay(protocolo.id)
        
        return protocolo
```

### Views

```python
# apps/protocolos/views.py
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Protocolo
from .serializers import (
    ProtocoloListSerializer,
    ProtocoloDetailSerializer,
    CriarProtocoloSerializer
)

class ProtocoloViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'tipo', 'categoria']
    ordering_fields = ['criado_em', 'atualizado_em']
    
    def get_queryset(self):
        return Protocolo.objects.filter(usuario=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CriarProtocoloSerializer
        elif self.action == 'retrieve':
            return ProtocoloDetailSerializer
        return ProtocoloListSerializer
    
    @action(detail=True, methods=['get'])
    def similares(self, request, pk=None):
        """Busca protocolos similares usando pgvector"""
        protocolo = self.get_object()
        
        # Query usando similaridade de embeddings
        similares = Protocolo.objects.filter(
            tipo=protocolo.tipo
        ).exclude(
            id=protocolo.id
        ).order_by(
            protocolo.embedding.cosine_distance('embedding')
        )[:5]
        
        serializer = ProtocoloListSerializer(similares, many=True, context={'request': request})
        return Response(serializer.data)
```

## 🤖 Implementação do Assistente IA

### Celery Tasks

```python
# apps/zeladoria/tasks.py
from celery import shared_task
from openai import OpenAI
from .models import Protocolo

@shared_task
def analisar_protocolo_ia(protocolo_id):
    """Analisa protocolo com NLP e gera embedding"""
    protocolo = Protocolo.objects.get(id=protocolo_id)
    
    client = OpenAI()
    
    # Gerar embedding
    response = client.embeddings.create(
        input=protocolo.descricao,
        model="text-embedding-ada-002"
    )
    
    protocolo.embedding = response.data[0].embedding
    protocolo.save()
    
    # Buscar protocolos similares e clusterizar
    # ...

@shared_task
def transcrever_audio(anexo_id):
    """Transcreve áudio usando Whisper"""
    anexo = AnexoProtocolo.objects.get(id=anexo_id)
    
    client = OpenAI()
    
    with open(anexo.arquivo.path, 'rb') as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    
    # Atualizar descrição do protocolo
    protocolo = anexo.protocolo
    protocolo.descricao += f"\n\n[Transcrição de áudio]: {transcript.text}"
    protocolo.save()
```

### Assistente API

```python
# apps/zeladoria/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from openai import OpenAI

@api_view(['POST'])
def analisar_relato(request):
    """Analisa relato do cidadão com NLP"""
    texto = request.data.get('texto', '')
    
    client = OpenAI()
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": """Você é um assistente que analisa relatos de zeladoria urbana.
                Extraia: categoria, endereço detectado, urgência (baixa/media/alta).
                Retorne JSON: {"categoria": "...", "endereco": "...", "urgencia": "..."}"""
            },
            {"role": "user", "content": texto}
        ],
        response_format={"type": "json_object"}
    )
    
    analise = json.loads(response.choices[0].message.content)
    
    return Response(analise)
```

## 🗺️ Geocoding

```python
# apps/zeladoria/views.py
from geopy.geocoders import Nominatim

@api_view(['GET'])
def geocode_reverso(request):
    """Converte coordenadas em endereço"""
    lat = request.query_params.get('latitude')
    lng = request.query_params.get('longitude')
    
    geolocator = Nominatim(user_agent="sinapse")
    location = geolocator.reverse(f"{lat}, {lng}")
    
    return Response({
        'endereco_completo': location.address,
        # ... parse do endereço
    })
```

## ⚙️ Configuração

### settings.py

```python
# config/settings/base.py

# CORS
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "https://sinapse.gov.br"
]

# JWT
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}

# Celery
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

# OpenAI
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Storage (AWS S3 ou similar)
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_STORAGE_BUCKET_NAME = 'sinapse-protocolos'
```

## 🚀 Deploy

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  db:
    image: postgis/postgis:15-3.3
    environment:
      POSTGRES_DB: sinapse
      POSTGRES_USER: sinapse
      POSTGRES_PASSWORD: senha_segura
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine

  backend:
    build: .
    command: gunicorn config.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - ./:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis

  celery:
    build: .
    command: celery -A config worker -l info
    depends_on:
      - db
      - redis

volumes:
  postgres_data:
```

---

**Este documento deve ser atualizado conforme a implementação evolui.**
