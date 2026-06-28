import pandas as pd, numpy as np
from scipy import stats
import re

pd.set_option('display.max_rows', 200)
pd.set_option('display.width', 160)

path = r"../Case Analista de Dados — the news [Dataset Palavritas].xlsx"
xls = pd.read_excel(path, sheet_name=None)
s = xls['palavritas_sessions'].copy()
a = xls['palavritas_attempts'].copy()
u = xls['user_profile'].copy()

log = []
def L(msg):
    log.append(msg)
    print(msg)

n0 = len(s)
L(f"=== SESSIONS: start {n0} rows ===")

# 1. drop exact duplicate rows
before = len(s)
s = s.drop_duplicates()
L(f"1. Dropped {before-len(s)} exact duplicate session rows -> {len(s)}")

# 2. normalize device casing
s['device'] = s['device'].str.lower().map({'android':'Android','ios':'iOS'})
L(f"2. Normalized device casing: {s['device'].value_counts().to_dict()}")

# 3. parse word_date mixed formats
def parse_date(x):
    if re.match(r'^\d{4}-\d{2}-\d{2}$', x):
        return pd.to_datetime(x, format='%Y-%m-%d')
    if re.match(r'^\d{2}/\d{2}/\d{4}$', x):
        return pd.to_datetime(x, format='%d/%m/%Y')
    return pd.NaT
s['word_date_parsed'] = s['word_date'].apply(parse_date)
L(f"3. Parsed word_date (mixed YYYY-MM-DD / DD/MM/YYYY): {s['word_date_parsed'].isna().sum()} unparseable")

# 4. time_to_complete_sec: null out non-positive (broken timer), keep row
bad_time = (s['time_to_complete_sec'] <= 0)
L(f"4. Nulling {bad_time.sum()} non-positive time_to_complete_sec values (kept rows)")
s.loc[bad_time, 'time_to_complete_sec'] = np.nan

# 5. attempts domain: valid is 1-6. Drop rows with attempts==0 or >6 (game rule violation) AND result null
invalid_attempts = ~s['attempts'].between(1,6)
L(f"5. Found {invalid_attempts.sum()} rows with attempts outside 1-6 (impossible per game rules: max 6 tries)")
result_null = s['result'].isna()
L(f"   Found {result_null.sum()} rows with null result")
drop_mask = invalid_attempts | result_null
L(f"   Dropping union of both = {drop_mask.sum()} corrupted rows ({drop_mask.sum()/len(s)*100:.2f}%)")
s = s[~drop_mask].copy()
L(f"   Sessions remaining: {len(s)}")

# 6. cross-check attempts field vs attempts table (informational only, not fixed)
real_counts = a.groupby('session_id')['attempt_number'].max().rename('real_attempts')
chk = s[['session_id','attempts']].merge(real_counts, on='session_id', how='left')
mismatch = (chk['attempts'] != chk['real_attempts']).sum()
L(f"6. INFO ONLY: {mismatch} sessions where sessions.attempts != max(attempt_number) in attempts table (~{mismatch/len(s)*100:.2f}%) - left as-is, flagged as known limitation")

L(f"\n=== SESSIONS clean final: {len(s)} rows (dropped {n0-len(s)} total, {(n0-len(s))/n0*100:.1f}%) ===\n")

# ATTEMPTS table cleaning
na0 = len(a)
a = a.drop_duplicates()
L(f"ATTEMPTS: dropped {na0-len(a)} exact duplicate rows -> {len(a)}")
bad_guess = ~a['guess'].str.len().eq(5)
L(f"ATTEMPTS: {bad_guess.sum()} rows with guess length != 5 (corrupted) - dropping")
a = a[~bad_guess].copy()

# USER PROFILE cleaning
L(f"\n=== USER_PROFILE: start {len(u)} rows ===")
# fix known mojibake (source encoding corruption, byte loss -> manual reconstruction from context)
sector_fix = {'finan�as':'financas','educa��o':'educacao','sa�de':'saude',
              'tech':'tech','outros':'outros','varejo':'varejo','direito':'direito','marketing':'marketing'}
u['sector'] = u['sector'].map(sector_fix).fillna(u['sector'])
u['salary_range'] = u['salary_range'].str.replace('at�', 'ate', regex=False)
u['job_role'] = u['job_role'].str.replace('S�nior', 'Senior', regex=False)
u['state'] = u['state'].replace({'S�o Paulo':'SP','Minas Gerais':'MG'})
L("Fixed mojibake (corrupted UTF-8 bytes) in sector/salary_range/job_role/state via manual mapping")

u['job_role'] = u['job_role'].str.strip().str.title()
L(f"Normalized job_role casing: {sorted(u['job_role'].unique())}")

def fix_food(x):
    if isinstance(x, bool): return x
    if isinstance(x, str):
        return x.lower() in ('sim','true')
    return x
u['orders_food_delivery'] = u['orders_food_delivery'].apply(fix_food)
L(f"Standardized orders_food_delivery to boolean: {u['orders_food_delivery'].value_counts().to_dict()}")

L(f"Missing values remaining: age_range={u['age_range'].isna().sum()}, city={u['city'].isna().sum()}, salary_range={u['salary_range'].isna().sum()} (kept as NaN - legitimate survey non-response)")

n_users_sessions = s['user_id'].nunique()
n_users_profile = u['user_id'].nunique()
L(f"\nNOTE: {n_users_sessions} unique users in sessions vs {n_users_profile} in profile -> {n_users_sessions-n_users_profile} users have NO profile data (only 800/1200 answered survey). Profile-based cuts only cover ~67% of users.")

s.to_csv('sessions_clean.csv', index=False)
a.to_csv('attempts_clean.csv', index=False)
u.to_csv('user_profile_clean.csv', index=False)
L("\nSaved cleaned CSVs.")

with open('cleaning_log.txt','w',encoding='utf-8') as f:
    f.write('\n'.join(log))
