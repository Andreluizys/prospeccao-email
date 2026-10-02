"""Junta os e-mails gerados (emails.jsonl) na planilha de revisão/envio (emails.xlsx).

Uso:
  python planilha.py                       (emails.jsonl -> emails.xlsx)
  python planilha.py --jsonl lote2.jsonl --xlsx emails.xlsx

Não duplica: se o e-mail de destino já está na planilha, a linha é ignorada.
Linhas já existentes (e o Status delas) nunca são alteradas.
"""
import argparse, json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill

COLUNAS = ['E-mail', 'Empresa', 'Contato', 'Site', 'Segmento', 'Nicho', 'Assunto', 'Corpo do e-mail',
           'Status', 'Observação']
LARGURAS = [32, 28, 18, 30, 22, 30, 45, 80, 20, 30]

p = argparse.ArgumentParser()
p.add_argument('--jsonl', default='emails.jsonl')
p.add_argument('--xlsx', default='emails.xlsx')
a = p.parse_args()

xlsx = Path(a.xlsx)
if xlsx.exists():
    wb = openpyxl.load_workbook(xlsx)
    ws = wb['Emails']
else:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Emails'
    ws.append(COLUNAS)
    for c, w in zip(ws[1], LARGURAS):
        c.font = Font(bold=True, color='FFFFFF')
        c.fill = PatternFill('solid', fgColor='1F4E78')
        ws.column_dimensions[c.column_letter].width = w
    ws.freeze_panes = 'A2'

col = {c.value: i for i, c in enumerate(ws[1])}
existentes = {str(r[col['E-mail']] or '').lower() for r in ws.iter_rows(min_row=2, values_only=True)}

novos = sem_email = 0
for linha in Path(a.jsonl).read_text(encoding='utf-8').splitlines():
    if not linha.strip():
        continue
    e = json.loads(linha)
    email = (e.get('email') or '').strip().lower()
    if not email and e.get('status') != 'Descartado':
        sem_email += 1
    if email and email in existentes:
        continue
    existentes.add(email)
    ws.append([email, e.get('empresa'), e.get('contato'), e.get('site'), e.get('segmento'), e.get('nicho'),
               e.get('assunto'), e.get('corpo'), e.get('status') or 'Rascunho', e.get('observacao')])
    for c in ws[ws.max_row]:
        c.alignment = Alignment(wrap_text=True, vertical='top')
    novos += 1

ws.auto_filter.ref = ws.dimensions
wb.save(xlsx)
print(f'{novos} linha(s) nova(s) em {xlsx}' + (f' ({sem_email} sem e-mail de destino)' if sem_email else ''))
print('Revise a planilha: troque o Status para "Não enviar" no que não quiser mandar.')
