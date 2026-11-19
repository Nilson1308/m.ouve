# Backend Implementation Checklist

Checklist completo para implementação do backend Django conforme especificações do frontend.

---

## 📋 Setup Inicial

### 1. Ambiente e Dependências

- [ ] Python 3.11+ instalado
- [ ] PostgreSQL 15+ com PostGIS instalado
- [ ] Redis instalado
- [ ] Criar ambiente virtual Python
- [ ] Instalar dependências base:
  ```bash
  pip install Django djangorestframework djangorestframework-simplejwt
  pip install django-cors-headers psycopg2-binary django-filter
  pip install celery redis python-decouple
  pip install openai geopy Pillow
  ```
- [ ] Criar estrutura de projeto Django
- [ ] Configurar settings (dev/prod split)
- [ ] Configurar CORS para frontend

### 2. Banco de Dados

- [ ] Criar database PostgreSQL
- [ ] Ativar extensões:
  ```sql
  CREATE EXTENSION IF NOT EXISTS postgis;
  CREATE EXTENSION IF NOT EXISTS vector;
  ```
- [ ] Configurar connection strings
- [ ] Testar conexão

---

## 🔐 Autenticação

### Models

- [ ] Criar model `Usuario` (AbstractUser)
  - [ ] Campo `cpf` (unique)
  - [ ] Campo `telefone`
  - [ ] Campo `metodo_autenticacao`
  - [ ] Campo `govbr_sub`
  - [ ] Timestamps (created_at, updated_at)

### Serializers

- [ ] `UsuarioSerializer`
- [ ] `LoginResponseSerializer`
- [ ] `RegisterSerializer`

### Views/ViewSets

- [ ] POST `/auth/register` - Cadastro padrão
- [ ] POST `/auth/login` - Login padrão
- [ ] POST `/auth/logout` - Logout
- [ ] POST `/auth/refresh` - Refresh token
- [ ] GET `/auth/govbr/authorize` - Redirecionar Gov.br
- [ ] POST `/auth/govbr/callback` - Callback Gov.br
- [ ] POST `/auth/sso-municipal/callback` - SSO Municipal

### Testes

- [ ] Teste de registro
- [ ] Teste de login
- [ ] Teste de refresh token
- [ ] Teste de logout
- [ ] Teste de JWT inválido

---

## 📝 Protocolos

### Models

- [ ] Model `Categoria`
  - [ ] Nome
  - [ ] Tipo (ouvidoria/zeladoria)
  - [ ] Ícone
  - [ ] Subcategorias (JSON ou FK)

- [ ] Model `Protocolo`
  - [ ] ID custom (PROT-2024-001)
  - [ ] FK para Usuario
  - [ ] FK para Categoria
  - [ ] Tipo (ouvidoria/zeladoria)
  - [ ] Descrição
  - [ ] Status
  - [ ] Endereço
  - [ ] Localização (PointField)
  - [ ] FK para Equipe (nullable)
  - [ ] Embedding (VectorField)
  - [ ] Timestamps

- [ ] Model `HistoricoProtocolo`
  - [ ] FK para Protocolo
  - [ ] Status
  - [ ] Descrição
  - [ ] FK para Usuario (quem fez)
  - [ ] Timestamp

- [ ] Model `AnexoProtocolo`
  - [ ] FK para Protocolo
  - [ ] Arquivo (FileField)
  - [ ] Tipo MIME
  - [ ] Timestamp

- [ ] Model `Equipe`
  - [ ] Nome
  - [ ] Tipo de atendimento
  - [ ] Membros (M2M com Usuario)

### Serializers

- [ ] `CategoriaSerializer`
- [ ] `ProtocoloListSerializer`
- [ ] `ProtocoloDetailSerializer`
- [ ] `CriarProtocoloSerializer`
- [ ] `AnexoSerializer`
- [ ] `HistoricoSerializer`

### ViewSets

- [ ] `ProtocoloViewSet`
  - [ ] list - GET `/protocolos`
  - [ ] retrieve - GET `/protocolos/{id}`
  - [ ] create - POST `/protocolos`
  - [ ] Filtros (status, tipo, categoria)
  - [ ] Paginação
  - [ ] Ordenação

- [ ] Action: GET `/protocolos/{id}/similares`
- [ ] Action: POST `/protocolos/{id}/comentarios`

### Validações

- [ ] Validar campos obrigatórios
- [ ] Validar formato de coordenadas
- [ ] Validar tamanho de arquivos
- [ ] Validar tipos de arquivo (imagens, áudio)

### Testes

- [ ] Teste de criação de protocolo
- [ ] Teste de listagem (com filtros)
- [ ] Teste de busca por ID
- [ ] Teste de upload de arquivos
- [ ] Teste de permissões (usuário só vê seus protocolos)

---

## 🤖 Zeladoria + IA

### Services/Tasks

- [ ] Celery configurado
- [ ] Task: `analisar_protocolo_ia`
  - [ ] Gerar embedding com OpenAI
  - [ ] Salvar no banco
  - [ ] Buscar similares

- [ ] Task: `transcrever_audio`
  - [ ] Usar Whisper API
  - [ ] Atualizar descrição do protocolo

- [ ] Service: Análise NLP
  - [ ] Extrair categoria
  - [ ] Extrair endereço
  - [ ] Determinar urgência

### Views

- [ ] POST `/zeladoria/assistente/analisar`
  - [ ] Recebe texto
  - [ ] Retorna categoria, endereço, urgência

- [ ] POST `/zeladoria/assistente/transcrever`
  - [ ] Recebe arquivo de áudio
  - [ ] Retorna transcrição

- [ ] GET `/zeladoria/geocode/reverse`
  - [ ] Query params: latitude, longitude
  - [ ] Retorna endereço formatado

- [ ] GET `/zeladoria/geocode/search`
  - [ ] Query param: query (endereço)
  - [ ] Retorna coordenadas

- [ ] GET `/zeladoria/categorias`
  - [ ] Lista categorias de zeladoria

### Integrações

- [ ] OpenAI API key configurada
- [ ] Whisper para transcrição
- [ ] GPT-4 para análise
- [ ] Embeddings (text-embedding-ada-002)
- [ ] Geopy para geocoding
- [ ] Nominatim configurado

### Testes

- [ ] Teste de transcrição (mock)
- [ ] Teste de análise NLP (mock)
- [ ] Teste de geocoding
- [ ] Teste de busca de similares

---

## 📢 Ouvidoria

### Models

- [ ] Model `Manifestacao` (ou usar Protocolo?)
  - [ ] Tipo manifestação (denúncia, reclamação, etc)

### Views

- [ ] GET `/ouvidoria/categorias`
  - [ ] Lista categorias de ouvidoria

### Testes

- [ ] Teste de criação de manifestação
- [ ] Teste de listagem de categorias

---

## 🔔 Notificações

### Models

- [ ] Model `Notificacao`
  - [ ] FK para Usuario
  - [ ] Título
  - [ ] Mensagem
  - [ ] FK para Protocolo (nullable)
  - [ ] Lida (bool)
  - [ ] Timestamp

- [ ] Model `TokenPush`
  - [ ] FK para Usuario
  - [ ] Token FCM
  - [ ] Plataforma (web/android/ios)
  - [ ] Ativo (bool)

### Services

- [ ] Firebase Cloud Messaging configurado
- [ ] Service para enviar push
- [ ] Service para enviar email (opcional)

### Views

- [ ] GET `/notificacoes`
  - [ ] Lista notificações do usuário
  - [ ] Filtro: lidas/não lidas

- [ ] PATCH `/notificacoes/{id}/ler`
  - [ ] Marca como lida

- [ ] POST `/notificacoes/registro-push`
  - [ ] Registra token FCM

### Tasks Celery

- [ ] Task: Enviar notificação push
- [ ] Task: Enviar email

### Triggers

- [ ] Notificar ao criar protocolo
- [ ] Notificar ao mudar status
- [ ] Notificar ao resolver protocolo

### Testes

- [ ] Teste de listagem
- [ ] Teste de marcar como lida
- [ ] Teste de registro de token

---

## 📊 Admin/Estatísticas

### Views

- [ ] GET `/admin/estatisticas`
  - [ ] Query params: data_inicio, data_fim, tipo
  - [ ] Retorna:
    - Total de protocolos
    - Por status
    - Por categoria
    - Tempo médio de resolução
    - Taxa de resolução

### Permissões

- [ ] Criar grupo "Gestor"
- [ ] Permission class para endpoints admin
- [ ] Apenas usuários gestores podem acessar

### Testes

- [ ] Teste de acesso autorizado
- [ ] Teste de acesso negado
- [ ] Teste de cálculos de métricas

---

## 🗺️ Geoespacial (PostGIS)

### Queries

- [ ] Buscar protocolos próximos a uma coordenada
  ```python
  Protocolo.objects.filter(
      localizacao__distance_lte=(point, D(km=5))
  )
  ```

- [ ] Buscar protocolos em um polígono
  ```python
  Protocolo.objects.filter(
      localizacao__within=polygon
  )
  ```

### Indexes

- [ ] Index GIST em `localizacao`
- [ ] Index em `status`
- [ ] Index em `tipo`
- [ ] Composite index: (`usuario_id`, `status`)

### Testes

- [ ] Teste de busca por proximidade
- [ ] Teste de busca em área

---

## 🔍 Busca e RAG

### pgvector

- [ ] Extension instalada
- [ ] Campo `embedding` no model Protocolo
- [ ] Index IVFFLAT ou HNSW

### Queries

- [ ] Busca por similaridade
  ```python
  Protocolo.objects.order_by(
      protocolo.embedding.cosine_distance('embedding')
  )
  ```

- [ ] Clusterização de protocolos similares

### Testes

- [ ] Teste de geração de embedding
- [ ] Teste de busca por similaridade

---

## 📤 Upload de Arquivos

### Storage

- [ ] Configurar AWS S3 (ou similar)
  ```python
  DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
  ```

- [ ] Ou usar storage local (dev)
  ```python
  MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
  MEDIA_URL = '/media/'
  ```

### Validações

- [ ] Validar tamanho (max 10MB por foto)
- [ ] Validar tipo MIME
- [ ] Validar número de arquivos (max 5 fotos)
- [ ] Gerar thumbnails (opcional)

### Testes

- [ ] Teste de upload de imagem
- [ ] Teste de upload de áudio
- [ ] Teste de validação de tamanho
- [ ] Teste de validação de tipo

---

## 🔒 Segurança

### Configurações

- [ ] DEBUG = False em produção
- [ ] SECRET_KEY segura (não commitada)
- [ ] ALLOWED_HOSTS configurado
- [ ] CORS_ALLOWED_ORIGINS configurado
- [ ] CSRF protection habilitado
- [ ] HTTPS obrigatório em produção

### Rate Limiting

- [ ] Instalar django-ratelimit
- [ ] Rate limit em endpoints de autenticação
- [ ] Rate limit em criação de protocolos

### Permissões

- [ ] Permission classes em todas as views
- [ ] Validar propriedade do recurso
- [ ] Sanitização de inputs

### Testes

- [ ] Teste de acesso não autorizado
- [ ] Teste de XSS
- [ ] Teste de SQL injection (ORM protege)
- [ ] Teste de CSRF

---

## 📝 Documentação

### OpenAPI/Swagger

- [ ] Instalar drf-spectacular
  ```bash
  pip install drf-spectacular
  ```

- [ ] Configurar em settings
- [ ] Adicionar docstrings em views
- [ ] Gerar schema
- [ ] Servir docs em `/api/schema/`

### Postman

- [ ] Criar collection Postman
- [ ] Exportar para JSON
- [ ] Incluir no repositório

---

## 🧪 Testes

### Coverage

- [ ] pytest e pytest-django instalados
- [ ] Coverage mínimo: 80%
- [ ] Testes de modelos
- [ ] Testes de serializers
- [ ] Testes de views
- [ ] Testes de permissions
- [ ] Testes de integração

### CI/CD

- [ ] GitHub Actions configurado
- [ ] Rodar testes em PR
- [ ] Verificar coverage
- [ ] Linting (flake8/black)

---

## 🚀 Deploy

### Docker

- [ ] Dockerfile criado
- [ ] docker-compose.yml
- [ ] Services: web, db, redis, celery
- [ ] Variáveis de ambiente
- [ ] Health checks

### Heroku/Railway/AWS

- [ ] Procfile
- [ ] runtime.txt
- [ ] requirements.txt
- [ ] Migrations automáticas
- [ ] Static files (whitenoise)

### Monitoramento

- [ ] Sentry configurado
- [ ] Logs estruturados
- [ ] Métricas de performance
- [ ] Alertas de erro

---

## ✅ Checklist Final

### Antes de Conectar Frontend

- [ ] Todos os endpoints do `API_CONTRACT.md` implementados
- [ ] Testes passando (>80% coverage)
- [ ] Documentação Swagger gerada
- [ ] CORS configurado para frontend
- [ ] Variáveis de ambiente documentadas
- [ ] Seeds/fixtures criados para desenvolvimento
- [ ] README do backend atualizado

### Integração

- [ ] Frontend conectado aos endpoints reais
- [ ] Mocks removidos das stores Pinia
- [ ] Testes E2E frontend+backend
- [ ] Performance testada
- [ ] Tratamento de erros validado

---

## 📚 Recursos

### Documentação

- [Django](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [PostGIS](https://postgis.net/)
- [pgvector](https://github.com/pgvector/pgvector)
- [Celery](https://docs.celeryproject.org/)
- [OpenAI API](https://platform.openai.com/docs)

### Exemplos

```python
# Exemplo de ViewSet completo
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

class ProtocoloViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'tipo']
    ordering_fields = ['criado_em']
    
    def get_queryset(self):
        return Protocolo.objects.filter(usuario=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CriarProtocoloSerializer
        elif self.action == 'retrieve':
            return ProtocoloDetailSerializer
        return ProtocoloListSerializer
```

---

**Use este checklist para rastrear o progresso da implementação do backend.**

**Status:** ⬜ Não iniciado | 🔄 Em progresso | ✅ Completo
