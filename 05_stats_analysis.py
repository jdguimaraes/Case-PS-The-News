import pandas as pd, numpy as np
from scipy import stats

pd.set_option('display.max_rows', 300)
pd.set_option('display.width', 160)

s = pd.read_csv('sessions_clean.csv', parse_dates=['word_date_parsed'])
u = pd.read_csv('user_profile_clean.csv')
s['played_next_day'] = s['played_next_day'].astype(bool)
s['active_d30'] = s['active_d30'].astype(bool)
s['newsletter_open_before_game'] = s['newsletter_open_before_game'].astype(bool)

out = []
def P(x=''):
    out.append(str(x))
    print(x)

def chi2_test(df, col, target):
    ct = pd.crosstab(df[col], df[target])
    chi2, p, dof, _ = stats.chi2_contingency(ct)
    rate = df.groupby(col)[target].mean()
    n = df.groupby(col)[target].count()
    P(f"-- {col} vs {target} -- chi2={chi2:.2f}, p={p:.6f}, dof={dof}")
    P(pd.DataFrame({'rate':rate, 'n':n}).sort_values('rate', ascending=False).to_string())
    P()
    return p

def ttest_cont(df, col, target):
    g1 = df[df[target]==True][col].dropna()
    g0 = df[df[target]==False][col].dropna()
    t, p = stats.ttest_ind(g1, g0, equal_var=False)
    P(f"-- {col} vs {target} -- mean(True)={g1.mean():.2f} mean(False)={g0.mean():.2f} t={t:.2f} p={p:.6f}")
    P()
    return p

P("="*90)
P("ANALISE 1: PLAYED_NEXT_DAY (retencao D+1)")
P("="*90)

P("\n### Horario de jogo (session_hour) ###")
ttest_cont(s, 'session_hour', 'played_next_day')
s['hour_bucket'] = pd.cut(s['session_hour'], bins=[5,9,12,17,21,24], labels=['manha cedo(6-9)','manha(10-12)','tarde(13-17)','noite(18-21)','madrugada(22-23)'])
chi2_test(s, 'hour_bucket', 'played_next_day')

P("\n### Palavra do dia (word) - top/bottom 10 por retencao D+1 ###")
chi2_test(s, 'word', 'played_next_day')

P("\n### Device ###")
chi2_test(s, 'device', 'played_next_day')

P("\n### Streak day ###")
ttest_cont(s, 'streak_day', 'played_next_day')

P("\n### Newsletter aberta antes do jogo ###")
chi2_test(s, 'newsletter_open_before_game', 'played_next_day')

P("\n### Resultado (win/lose) ###")
chi2_test(s, 'result', 'played_next_day')

P("\n### Numero de tentativas ###")
ttest_cont(s, 'attempts', 'played_next_day')

P("\n### Tempo de jogo ###")
ttest_cont(s, 'time_to_complete_sec', 'played_next_day')

su = s.merge(u, on='user_id', how='left')
P("\n### Setor (sector) - apenas usuarios com perfil ###")
chi2_test(su.dropna(subset=['sector']), 'sector', 'played_next_day')

P("\n### Faixa salarial ###")
chi2_test(su.dropna(subset=['salary_range']), 'salary_range', 'played_next_day')

P("\n### Pede food delivery ###")
chi2_test(su.dropna(subset=['orders_food_delivery']), 'orders_food_delivery', 'played_next_day')

P("\n### Frequencia food delivery/semana ###")
ttest_cont(su, 'food_delivery_freq_week', 'played_next_day')

P("\n### Assinante newsletter (perfil) ###")
chi2_test(su.dropna(subset=['newsletter_subscriber']), 'newsletter_subscriber', 'played_next_day')

P("\n### Joga outros jogos de palavras ###")
chi2_test(su.dropna(subset=['plays_other_word_games']), 'plays_other_word_games', 'played_next_day')

P("\n\n" + "="*90)
P("ANALISE 2: ACTIVE_D30 (retencao 30 dias)")
P("="*90)

P("\n### Horario de jogo ###")
chi2_test(s, 'hour_bucket', 'active_d30')

P("\n### Streak day ###")
ttest_cont(s, 'streak_day', 'active_d30')

P("\n### Newsletter aberta antes do jogo ###")
chi2_test(s, 'newsletter_open_before_game', 'active_d30')

P("\n### Resultado (win/lose) ###")
chi2_test(s, 'result', 'active_d30')

P("\n### Played next day -> active d30 ###")
chi2_test(s, 'played_next_day', 'active_d30')

P("\n### Device ###")
chi2_test(s, 'device', 'active_d30')

P("\n### Setor ###")
chi2_test(su.dropna(subset=['sector']), 'sector', 'active_d30')

P("\n### Faixa salarial ###")
chi2_test(su.dropna(subset=['salary_range']), 'salary_range', 'active_d30')

P("\n### Food delivery ###")
chi2_test(su.dropna(subset=['orders_food_delivery']), 'orders_food_delivery', 'active_d30')
ttest_cont(su, 'food_delivery_freq_week', 'active_d30')

P("\n### Newsletter subscriber (perfil) ###")
chi2_test(su.dropna(subset=['newsletter_subscriber']), 'newsletter_subscriber', 'active_d30')

P("\n### typical_play_time (perfil declarado) vs active_d30 ###")
chi2_test(su.dropna(subset=['typical_play_time']), 'typical_play_time', 'active_d30')

with open('stats_results.txt','w',encoding='utf-8') as f:
    f.write('\n'.join(out))
