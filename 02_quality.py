import pandas as pd
pd.set_option('display.max_rows', 200)
path = r"../Case Analista de Dados — the news [Dataset Palavritas].xlsx"
xls = pd.read_excel(path, sheet_name=None)
s = xls['palavritas_sessions']
a = xls['palavritas_attempts']
u = xls['user_profile']

print("### sessions: value ranges / uniques ###")
print("attempts:", sorted(s['attempts'].unique()))
print("result:", s['result'].unique(), s['result'].value_counts(dropna=False))
print("device:", s['device'].unique())
print("session_hour range:", s['session_hour'].min(), s['session_hour'].max())
print("streak_day range:", s['streak_day'].min(), s['streak_day'].max())
print("time_to_complete_sec describe:\n", s['time_to_complete_sec'].describe())
print("word_date min/max:", s['word_date'].min(), s['word_date'].max())
print("word_date dtype sample:", s['word_date'].head(5).tolist())
print("n unique session_id:", s['session_id'].nunique(), "vs rows", len(s))
print("n unique user_id:", s['user_id'].nunique())
print("n unique words:", s['word'].nunique())

print("\n### full duplicate rows sample ###")
print(s[s.duplicated(keep=False)].sort_values('session_id').head(10))

print("\n### result null rows sample ###")
print(s[s['result'].isna()][['session_id','attempts','result']].head(10))

print("\n### attempts vs result consistency ###")
print(s.groupby('result')['attempts'].describe())

print("\n### negative/weird time_to_complete ###")
print((s['time_to_complete_sec']<=0).sum(), s['time_to_complete_sec'].min())
print((s['time_to_complete_sec']>3600).sum(), s['time_to_complete_sec'].max())

print("\n### session_id dup but different content? ###")
dup_ids = s['session_id'][s['session_id'].duplicated(keep=False)]
print(dup_ids.nunique(), "duplicated session_ids")

print("\n### attempts table: attempt_number range, guess length ###")
print(a['attempt_number'].min(), a['attempt_number'].max())
print(a['guess'].str.len().value_counts())
print("correct_positions range:", a['correct_positions'].min(), a['correct_positions'].max())
print("correct_letters range:", a['correct_letters'].min(), a['correct_letters'].max())
print("session_ids in attempts not in sessions:", (~a['session_id'].isin(s['session_id'])).sum())
print("session_ids in sessions not in attempts:", (~s['session_id'].isin(a['session_id'])).sum())

print("\n### user_profile categorical uniques ###")
for c in ['age_range','state','salary_range','job_role','sector','company_size','orders_food_delivery','food_delivery_platform','primary_device','typical_play_time']:
    print(c, u[c].unique()[:20])

print("\n### food_delivery_freq_week range ###")
print(u['food_delivery_freq_week'].describe())
print(u.groupby('orders_food_delivery')['food_delivery_freq_week'].describe())

print("\n### user_id overlap sessions vs profile ###")
print("users in sessions:", s['user_id'].nunique())
print("users in profile:", u['user_id'].nunique())
print("users in profile also in sessions:", u['user_id'].isin(s['user_id']).sum())
print("profile dup user_id:", u['user_id'].duplicated().sum())
