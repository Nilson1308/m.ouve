"""Upload, validação e remoção de avatar do usuário autenticado."""

import io

from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage
from django.test import TestCase, override_settings
from PIL import Image
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


def _imagem_bytes(fmt: str = "PNG", size=(32, 32)) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", size, color=(120, 80, 200)).save(buf, format=fmt)
    return buf.getvalue()


def _arquivo_imagem(nome: str, fmt: str = "PNG", content_type: str = "image/png") -> bytes:
    dados = _imagem_bytes(fmt)
    return dados


@override_settings(MEDIA_ROOT="/tmp/ouve_test_media_avatar")
class UsuarioAvatarTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.usuario = User.objects.create_user(
            cpf="39053344705",
            password="SenhaAntiga1!",
            nome="Cidadão Avatar",
            email="avatar.test@local",
        )
        self.client.force_authenticate(user=self.usuario)
        self.url = "/api/v1/auth/me/avatar"

    def _upload(self, nome, conteudo, content_type="image/png"):
        from django.core.files.uploadedfile import SimpleUploadedFile

        arquivo = SimpleUploadedFile(nome, conteudo, content_type=content_type)
        return self.client.post(self.url, {"avatar": arquivo}, format="multipart")

    def test_upload_imagem_valida(self):
        response = self._upload("foto.png", _arquivo_imagem("foto.png"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data.get("avatar"))
        self.assertIn("/media/avatars/", response.data["avatar"])
        self.usuario.refresh_from_db()
        self.assertTrue(self.usuario.avatar)

    def test_rejeita_arquivo_nao_imagem(self):
        from django.core.files.uploadedfile import SimpleUploadedFile

        arquivo = SimpleUploadedFile(
            "doc.txt", b"nao e imagem", content_type="text/plain"
        )
        response = self.client.post(self.url, {"avatar": arquivo}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        detalhe = response.data.get("avatar") or (
            response.data.get("error", {}).get("details", {}).get("avatar")
        )
        self.assertIsNotNone(detalhe)

    def test_rejeita_arquivo_acima_de_2mb(self):
        from django.core.files.uploadedfile import SimpleUploadedFile

        grande = b"\xff\xd8\xff" + b"\x00" * (2 * 1024 * 1024)
        arquivo = SimpleUploadedFile("grande.jpg", grande, content_type="image/jpeg")
        response = self.client.post(self.url, {"avatar": arquivo}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("2 MB", str(response.data))

    def test_substituicao_remove_arquivo_anterior(self):
        r1 = self._upload("a.png", _arquivo_imagem("a.png"))
        self.assertEqual(r1.status_code, status.HTTP_200_OK)
        self.usuario.refresh_from_db()
        nome_anterior = self.usuario.avatar.name
        self.assertTrue(default_storage.exists(nome_anterior))

        r2 = self._upload(
            "b.webp",
            _imagem_bytes("WEBP"),
            content_type="image/webp",
        )
        self.assertEqual(r2.status_code, status.HTTP_200_OK)
        self.usuario.refresh_from_db()
        self.assertNotEqual(self.usuario.avatar.name, nome_anterior)
        self.assertFalse(default_storage.exists(nome_anterior))
        self.assertTrue(default_storage.exists(self.usuario.avatar.name))

    def test_remover_avatar_delete(self):
        self._upload("foto.png", _arquivo_imagem("foto.png"))
        self.usuario.refresh_from_db()
        nome = self.usuario.avatar.name

        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data.get("avatar"))
        self.usuario.refresh_from_db()
        self.assertFalse(self.usuario.avatar)
        self.assertFalse(default_storage.exists(nome))

    def test_remover_avatar_json_null(self):
        self._upload("foto.png", _arquivo_imagem("foto.png"))
        response = self.client.patch(self.url, {"avatar": None}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data.get("avatar"))

    def test_get_me_retorna_url_avatar(self):
        self._upload("foto.png", _arquivo_imagem("foto.png"))
        response = self.client.get("/api/v1/auth/me")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data.get("avatar"))