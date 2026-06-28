import pandas as pd, numpy as np
from scipy import stats

pd.set_option('display.max_rows', 300)
pd.set_option('display.width', 160)

s = pd.read_csv('sessions_clean.csv', parse_dates=['word_date_parsed'])
a = pd.read_csv('attempts_clean.csv')
s['played_next_day'] = s['played_next_day'].astype(bool)
s['active_d30'] = s['active_d30'].astype(bool)
s['newsletter_open_before_game'] = s['newsletter_open_before_game'].astype(bool)
s['hour_bucket'] = pd.cut(s['session_hour'], bins=[5,9,12,17,21,24],
    labels=['manha cedo(6-9)','manha(10-12)','tarde(13-17)','noite(18-21)','madrugada(22-23)'])

out = []
def P(x=''):
    out.append(str(x)); print(x)

def chi2_test(df, col, target):
    ct = pd.crosstab(df[col], df[target])
    chi2, p, dof, _ = stats.chi2_contingency(ct)
    rate = df.groupby(col)[target].mean(); n = df.groupby(col)[target].count()
    P(f"-- {col} vs {target} -- chi2={chi2:.2f}, p={p:.6f}, dof={dof}")
    P(pd.DataFrame({'rate':rate, 'n':n}).sort_values('rate', ascending=False).to_string())
    P()
    return p

def ttest_cont(df, col, target):
    g1 = df[df[target]==True][col].dropna(); g0 = df[df[target]==False][col].dropna()
    t, p = stats.ttest_ind(g1, g0, equal_var=False)
    P(f"-- {col} vs {target} -- mean(True)={g1.mean():.2f} mean(False)={g0.mean():.2f} t={t:.2f} p={p:.6f}")
    P()
    return p

P("="*90)
P("ANALISE COMPLEMENTAR 1: TABELA DE TENTATIVAS (attempts) x RETENCAO")
P("Motivo: a aba palavritas_attempts (146k linhas) traz o detalhe de cada palpite -")
P("numero da tentativa, letras certas, posicoes certas. Ate aqui so usamos o resultado")
P("binario (ganhou/perdeu). Aqui testamos se a EXPERIENCIA dentro do jogo (velocidade")
P("de acerto, quase-acerto na derrota) tambem explica o retorno.")
P("="*90)

# attempt_number da ultima tentativa de cada sessao = em quantas tentativas a sessao terminou
last_attempt = a.groupby('session_id')['attempt_number'].max().rename('attempts_used')
s2 = s.merge(last_attempt, on='session_id', how='left')

P("\n### Sessoes ganhas: tentativas usadas para ganhar (1=acertou de primeira ... 6=ganhou no limite) ###")
won = s2[s2['result'].str.lower().isin(['win','venceu','ganhou','won'])] if s2['result'].dtype == object else s2
# fallback: usa coluna result tal como limpa (valores ja conhecidos no dataset)
P(s2['result'].value_counts())

won = s2[s2['result'].astype(str).str.lower().str.contains('win|venceu|ganh', regex=True, na=False)]
P(f"\nsessoes consideradas vitoria: {len(won)} de {len(s2)}")
if len(won) > 0:
    ttest_cont(won, 'attempts_used', 'played_next_day')
    chi2_test(won, 'attempts_used', 'played_next_day')

P("\n### Sessoes perdidas: quao perto o usuario chegou (max correct_positions na ultima tentativa) ###")
lost = s2[~s2.index.isin(won.index)]
last_try = a.sort_values('attempt_number').groupby('session_id').tail(1)[['session_id','correct_positions','correct_letters']]
lost2 = lost.merge(last_try, on='session_id', how='left')
P(f"sessoes consideradas derrota: {len(lost2)}")
if lost2['correct_positions'].notna().sum() > 0:
    ttest_cont(lost2.dropna(subset=['correct_positions']), 'correct_positions', 'played_next_day')
    # near-miss: perdeu com 4 de 5 letras na posicao certa
    lost2['near_miss'] = lost2['correct_positions'] >= 4
    chi2_test(lost2.dropna(subset=['near_miss']), 'near_miss', 'played_next_day')

P("\n### Mesmo teste para active_d30 (efeito de longo prazo da experiencia de jogo) ###")
if len(won) > 0:
    chi2_test(won, 'attempts_used', 'active_d30')
if lost2['correct_positions'].notna().sum() > 0:
    chi2_test(lost2.dropna(subset=['near_miss']), 'near_miss', 'active_d30')

P("\n\n" + "="*90)
P("ANALISE COMPLEMENTAR 2: EFEITO COMPOSTO PARA D+1")
P("Motivo: para D30 achamos um efeito composto forte (newsletter aberta + voltou no D+1).")
P("Testamos aqui se um composto equivalente existe tambem para o D+1 isoladamente -")
P("ex.: jogar de manha E ganhar o jogo no mesmo dia.")
P("="*90)

P("\n### Ganhou x jogou de manha -> played_next_day ###")
s2['won'] = s2['result'].astype(str).str.lower().str.contains('win|venceu|ganh', regex=True, na=False)
s2['morning'] = s2['hour_bucket'].isin(['manha cedo(6-9)','manha(10-12)'])
combo = s2.groupby(['won','morning'])['played_next_day'].agg(['mean','count'])
P(combo)

P("\n### Newsletter aberta x ganhou -> played_next_day ###")
combo2 = s2.groupby(['newsletter_open_before_game','won'])['played_next_day'].agg(['mean','count'])
P(combo2)

P("\n### Newsletter aberta x jogou de manha -> played_next_day ###")
combo3 = s2.groupby(['newsletter_open_before_game','morning'])['played_next_day'].agg(['mean','count'])
P(combo3)

with open('attempts_analysis_results.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print("\nsaved attempts_analysis_results.txt")
