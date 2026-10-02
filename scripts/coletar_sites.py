"""Visita o site de cada cliente e junta o que interessa para escrever o e-mail.

Uso:
  python coletar_sites.py https://empresa1.com.br empresa2.com.br
  python coletar_sites.py --arquivo clientes.xlsx      (ou .csv / .txt, um site por linha)
  python coletar_sites.py --arquivo clientes.xlsx --saida pesquisa.jsonl --threads 8

Gera um JSONL (uma empresa por linha). Se rodar de novo, pula os sites já coletados.
"""
import argparse, csv, json, re, sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/130.0 Safari/537.36',
           'Accept-Language': 'pt-BR,pt;q=0.9'}
PAGINAS_UTEIS = re.compile(r'sobre|quem-?somos|empresa|institucional|historia|about|'
                           r'produto|servico|solucao|segmento|atuacao|contato|fale-?conosco', re.I)
RE_EMAIL = re.compile(r'[\w.+-]+@[\w-]+(?:\.[\w-]+)+')
RE_FONE = re.compile(r'\(?\b\d{2}\)?\s?9?\d{4}[-.\s]?\d{4}\b')
IGNORAR_EMAIL = re.compile(r'\.(png|jpe?g|gif|webp|svg)$|sentry|wixpress|example|seudominio|email@', re.I)
COLUNAS_SITE = ('site', 'url', 'website', 'endereço eletrônico', 'homepage', 'dominio', 'domínio')
PROVEDORES = ('gmail.', 'hotmail.', 'outlook.', 'yahoo.', 'uol.com', 'bol.com', 'terra.com', 'live.', 'icloud.')


def normalizar(url):
    url = (url or '').strip()
    if '@' in url:  # veio um e-mail: usa o domínio, menos se for gmail/hotmail etc.
        url = url.split('@', 1)[1]
        if url.lower().startswith(PROVEDORES):
            return None
    if not url or ' ' in url or '.' not in url:
        return None
    if not url.startswith('http'):
        url = 'https://' + url
    return url.rstrip('/')


def ler_entrada(arquivo):
    """Devolve lista de dicts com pelo menos 'site'; as outras colunas da planilha vão junto."""
    p = Path(arquivo)
    if p.suffix.lower() in ('.xlsx', '.xlsm'):
        import openpyxl
        ws = openpyxl.load_workbook(p, read_only=True, data_only=True).active
        linhas = list(ws.iter_rows(values_only=True))
        cab = [str(c or '').strip() for c in linhas[0]]
        dados = [dict(zip(cab, l)) for l in linhas[1:]]
    elif p.suffix.lower() == '.csv':
        with open(p, encoding='utf-8-sig', newline='') as f:
            amostra = f.read(4096); f.seek(0)
            dados = list(csv.DictReader(f, dialect=csv.Sniffer().sniff(amostra, ';,\t')))
        cab = list(dados[0]) if dados else []
    else:
        return [{'site': l.strip()} for l in p.read_text(encoding='utf-8').splitlines() if l.strip()]

    col_site = next((c for c in cab if c.lower() in COLUNAS_SITE), None)
    col_email = next((c for c in cab if 'mail' in c.lower()), None)
    if not col_site and not col_email:
        sys.exit(f'Não achei coluna de site nem de e-mail. Colunas: {cab}')
    saida = []
    for d in dados:
        d = {k: ('' if v is None else str(v).strip()) for k, v in d.items() if k}
        d['site'] = d.get(col_site) or d.get(col_email) or ''  # sem site, tenta o domínio do e-mail
        if d['site']:
            saida.append(d)
    return saida


def baixar(url, sessao):
    r = sessao.get(url, headers=HEADERS, timeout=15, allow_redirects=True)
    r.raise_for_status()
    if 'html' not in r.headers.get('Content-Type', 'html'):
        raise ValueError('não é HTML')
    r.encoding = r.apparent_encoding or r.encoding
    return r.url, BeautifulSoup(r.text, 'html.parser')


def texto_limpo(soup, limite):
    for t in soup(['script', 'style', 'noscript', 'svg', 'iframe', 'form']):
        t.decompose()
    return re.sub(r'\s+', ' ', soup.get_text(' ')).strip()[:limite]


def coletar(item, max_paginas=4):
    url = normalizar(item['site'])
    res = {**item, 'site': url, 'ok': False}
    if not url:
        res['erro'] = 'sem site (ou e-mail de provedor gratuito)'
        return res
    sessao = requests.Session()
    try:
        try:
            final, soup = baixar(url, sessao)
        except requests.exceptions.SSLError:
            final, soup = baixar(url.replace('https://', 'http://'), sessao)
    except Exception as e:
        res['erro'] = f'{type(e).__name__}: {e}'[:200]
        return res

    dominio = urlparse(final).netloc.removeprefix('www.')
    meta = soup.find('meta', attrs={'name': re.compile('description', re.I)})
    res.update(ok=True, site=final, dominio=dominio,
               titulo=(soup.title.get_text(strip=True) if soup.title else ''),
               descricao=(meta.get('content', '').strip() if meta else ''),
               titulos=[h.get_text(' ', strip=True) for h in soup.find_all(['h1', 'h2'])][:15])

    links = []
    for a in soup.find_all('a', href=True):
        href = urljoin(final, a['href']).split('#')[0]
        if urlparse(href).netloc.removeprefix('www.') == dominio and PAGINAS_UTEIS.search(href) \
                and href not in links and href.rstrip('/') != final.rstrip('/'):
            links.append(href)
    paginas = [('inicio', soup)]
    for link in links[:max_paginas]:
        try:
            paginas.append((urlparse(link).path or link, baixar(link, sessao)[1]))
        except Exception:
            pass
    sopas = [s for _, s in paginas]

    # contatos antes de limpar o HTML (rodapé, mailto, tel)
    emails, fones, redes = set(), set(), set()
    for s in sopas:
        emails |= {m.lower().rstrip('.') for m in RE_EMAIL.findall(str(s)) if not IGNORAR_EMAIL.search(m)}
        fones |= set(RE_FONE.findall(s.get_text(' ')))
        redes |= {urljoin(final, a['href']) for a in s.find_all('a', href=True)
                  if re.search(r'linkedin|instagram|facebook|wa\.me|whatsapp', a['href'], re.I)}
    res['paginas'] = {nome: texto_limpo(s, 2500 if i == 0 else 1500) for i, (nome, s) in enumerate(paginas)}
    res['emails_site'] = sorted(emails, key=lambda e: (dominio not in e, e))[:10]
    res['telefones'] = sorted(fones)[:5]
    res['redes'] = sorted(redes)[:6]
    return res


def main():
    p = argparse.ArgumentParser()
    p.add_argument('sites', nargs='*')
    p.add_argument('--arquivo')
    p.add_argument('--saida', default='pesquisa.jsonl')
    p.add_argument('--threads', type=int, default=6)
    p.add_argument('--paginas', type=int, default=4, help='páginas internas por site (sobre, produtos, contato...)')
    a = p.parse_args()

    itens = [{'site': s} for s in a.sites] + (ler_entrada(a.arquivo) if a.arquivo else [])
    if not itens:
        p.error('passe sites ou --arquivo')

    saida = Path(a.saida)
    feitos = set()
    if saida.exists():
        for l in saida.read_text(encoding='utf-8').splitlines():
            try:
                feitos.add(json.loads(l)['_entrada'])
            except Exception:
                pass
    vistos, fila = set(), []
    for it in itens:
        chave = it['site'].lower()
        if chave not in feitos and chave not in vistos:
            vistos.add(chave)
            fila.append({**it, '_entrada': chave})
    print(f'{len(fila)} site(s) para coletar ({len(feitos)} já estavam em {saida})')

    ok = 0
    with ThreadPoolExecutor(a.threads) as ex, open(saida, 'a', encoding='utf-8') as f:
        futuros = [ex.submit(coletar, it, a.paginas) for it in fila]
        for i, fut in enumerate(as_completed(futuros), 1):
            r = fut.result()
            f.write(json.dumps(r, ensure_ascii=False) + '\n'); f.flush()
            ok += r['ok']
            print(f"[{i}/{len(fila)}] {'OK ' if r['ok'] else 'ERRO'} {r['site'] or r['_entrada']}"
                  + ('' if r['ok'] else f"  ({r.get('erro')})"))
    print(f'Pronto: {ok} coletado(s), {len(fila) - ok} com erro. Arquivo: {saida}')


if __name__ == '__main__':
    main()
