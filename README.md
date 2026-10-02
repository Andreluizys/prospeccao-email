# prospeccao-email — skill do Claude Code

Você manda **um site, vários sites ou uma planilha de clientes**. A skill entra em cada site, descobre o segmento, o nicho e o contato da empresa, escreve um **e-mail de proposta comercial personalizado** para cada uma, monta uma planilha para você revisar e **envia pelo seu próprio e-mail** (UOL, UOL Host, Gmail, Outlook ou qualquer SMTP), em ritmo seguro para não cair em spam.

Feita para representantes comerciais e vendedores B2B que precisam mandar centenas ou milhares de e-mails sem escrever um por um.

## Como funciona

```
sites / planilha
   │  coletar_sites.py   → visita início, "sobre", "produtos", "contato"
   ▼
pesquisa.jsonl          (texto do site, e-mails, telefones, redes)
   │  Claude (ou gerar_com_api.py para milhares)
   ▼
emails.jsonl            (assunto + corpo personalizados por empresa)
   │  planilha.py
   ▼
emails.xlsx             ← você revisa, edita, aprova
   │  enviar.py         → SMTP do seu e-mail, limite diário, pausa entre envios
   ▼
Status "Enviado dd/mm/aaaa" na planilha
```

## Instalação

1. Tenha o [Claude Code](https://claude.com/claude-code) e o Python 3.10+ instalados.
2. Copie esta pasta para as suas skills:
   ```bash
   git clone https://github.com/SEU-USUARIO/prospeccao-email ~/.claude/skills/prospeccao-email
   ```
3. Instale as dependências:
   ```bash
   pip install -r ~/.claude/skills/prospeccao-email/requirements.txt
   ```
4. Copie `config.exemplo.json` para `config.json` e preencha com os seus dados (ou deixe o Claude perguntar e preencher na primeira vez).

## Uso

No Claude Code, dentro da pasta onde estão (ou vão ficar) suas planilhas:

> /prospeccao-email pesquisa esses sites e escreve os e-mails: metalurgicax.com.br, padariay.com.br

> /prospeccao-email usa a planilha clientes.xlsx

O Claude coleta os sites, escreve os e-mails, mostra alguns exemplos para você ajustar o tom e gera `emails.xlsx`. Depois você envia **no seu terminal**:

```bash
python ~/.claude/skills/prospeccao-email/scripts/enviar.py --teste seu-email@gmail.com
```

```bash
python ~/.claude/skills/prospeccao-email/scripts/enviar.py
```

A senha é pedida na hora e não fica salva. Rode o mesmo comando todo dia até acabar a lista; o script respeita o limite diário e nunca manda duas vezes para a mesma pessoa.

## Ligando o seu e-mail da UOL

No `config.json`, bloco `smtp`:

| Seu e-mail                                   | `provedor` | Servidor usado              |
|----------------------------------------------|------------|-----------------------------|
| Domínio próprio na UOL Host (voce@empresa.com.br) | `uolhost`  | smtps.uhserver.com : 465    |
| @uol.com.br                                  | `uol`      | smtps.uol.com.br : 465      |
| @bol.com.br                                  | `bol`      | smtps.bol.com.br : 465      |
| Gmail / Google Workspace (com senha de app)  | `gmail`    | smtp.gmail.com : 465        |
| Outlook / Microsoft 365                      | `outlook`  | smtp-mail.outlook.com : 587 |
| Outro (Brevo, Amazon SES, Mailgun...)        | — use `"host"` e `"porta"` | |

Se a porta 465 for recusada, o script tenta a 587 sozinho.

## Listas grandes (milhares de e-mails)

- **Escrita**: para não depender de conversa, use `scripts/gerar_com_api.py` com sua `ANTHROPIC_API_KEY` (custo por e-mail na sua conta da Anthropic). Teste com `--limite 10`.
- **Envio**: provedores de caixa postal (UOL, Gmail, Outlook) limitam envios por dia. Comece com 100–200/dia e aumente aos poucos. 8 mil e-mails levam semanas nesse ritmo. Para ir mais rápido sem trocar o remetente, use um serviço de disparo (Brevo, Amazon SES) autenticado no seu domínio e coloque o `host`/`porta` dele no config.
- Configure **SPF, DKIM e DMARC** no domínio. Sem isso, a maior parte cai em spam.

## Boas práticas e LGPD

- Mande só para e-mails corporativos, com oferta que tenha a ver com o negócio da empresa.
- Todo e-mail sai com linha de descadastro e cabeçalho `List-Unsubscribe`. Quem pedir para sair vai para `descadastro.txt` e nunca mais recebe.
- `config.json`, planilhas e arquivos `.jsonl` estão no `.gitignore`: seus dados e os dos seus clientes não sobem para o GitHub.

## Arquivos

| Arquivo | O que faz |
|---|---|
| `SKILL.md` | Instruções que o Claude segue |
| `instrucoes_email.md` | Regras de como escrever cada e-mail (edite para mudar o estilo) |
| `config.exemplo.json` | Modelo de configuração: você, sua oferta, assinatura, SMTP |
| `scripts/coletar_sites.py` | Visita os sites e extrai informações e contatos |
| `scripts/gerar_com_api.py` | (Opcional) escreve os e-mails em massa pela API |
| `scripts/planilha.py` | Junta os e-mails na planilha de revisão |
| `scripts/enviar.py` | Envia pelo seu SMTP com limite diário e controle de status |

## Licença

MIT
