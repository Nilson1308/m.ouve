# Materiais comerciais — M.Ouve

| Artefato | Uso |
|----------|-----|
| [`ONE_PAGER_MOOUVE.md`](ONE_PAGER_MOOUVE.md) | Texto completo (vendas, objeções, pacotes) |
| [`export/ONE_PAGER_MOOUVE.pdf`](export/ONE_PAGER_MOOUVE.pdf) | PDF para envio |
| [`ONE_PAGER_MOOUVE_SLIDES.md`](ONE_PAGER_MOOUVE_SLIDES.md) | Fonte Marp (slides) |
| [`export/ONE_PAGER_MOOUVE_SLIDES.pdf`](export/ONE_PAGER_MOOUVE_SLIDES.pdf) | Deck ~15 slides |
| [`PROPOSTA_MODELO_ANEXO_I_SERVICOS.md`](PROPOSTA_MODELO_ANEXO_I_SERVICOS.md) | Proposta + **Anexo I** (catálogo) |

## Regenerar PDFs

Requer Node.js, Google Chrome (Marp) e rede para `npx` na primeira execução.

```bash
cd docs/knowledge/comercial
npx @marp-team/marp-cli ONE_PAGER_MOOUVE_SLIDES.md --pdf -o export/ONE_PAGER_MOOUVE_SLIDES.pdf
npx md-to-pdf ONE_PAGER_MOOUVE.md && mv ONE_PAGER_MOOUVE.pdf export/
npx md-to-pdf PROPOSTA_MODELO_ANEXO_I_SERVICOS.md && mv PROPOSTA_MODELO_ANEXO_I_SERVICOS.pdf export/
```

Os PDFs versionados no Git devem ser atualizados quando o Markdown mudar de forma relevante para comercial.