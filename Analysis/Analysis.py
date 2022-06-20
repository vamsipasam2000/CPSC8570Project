# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.8
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# +
import pandas as pd
import seaborn as sns 
import numpy as np
import statsmodels.api as sm
import scipy.stats as stats
from scipy.stats import epps_singleton_2samp as epps
import matplotlib.pyplot as plt
import warnings
from math import floor
from mlxtend.evaluate import permutation_test

MIN_SAMPLE_SIZE = 20
MIN_SAMPLE_SIZE_2 = 45

pd.set_option('precision', 2)

sns.set(
    context="paper",
    style="darkgrid",
    rc={"figure.dpi": 150}
)
df = pd.read_pickle('complete_lifetimes_v4.pd')
df.c_lifetime = df.c_lifetime.astype(float)
df_code_age = pd.read_json('codelifetimes.json', orient='index') 

def plot_hist_trend_complete(project, estimator=np.mean, stats = False, min=1900, max=2021, data=df, field='lifetime', debug=False, fit_reg=False, lw=0, lp=True, xlim=True, ylim=(0, 2600), label='Lifetime', color=None, f=True, marker='x', ci='ci', latex=False):
    if f:
        f = plt.figure()
        f.set_figwidth(6)
        f.set_figheight(3)
    if project is None:
        df_proj = data
    else:
        df_proj = data.loc[data.project == project] 
    df_proj = df_proj.loc[df_proj.fix_year >= min].loc[df_proj.fix_year <= max]
    
    df_counts = df_proj[['fix_year', field]].groupby(by='fix_year').count()
    drop_years = list(df_counts.loc[df_counts[field] < MIN_SAMPLE_SIZE_2].index)
    if debug:
        print(df_counts)
    df_proj = df_proj.loc[~df_proj.fix_year.isin(drop_years)]
    
    
    ax = sns.regplot(data=df_proj, x='fix_year', y=field, x_estimator=estimator, x_ci=ci, marker=marker, truncate=False, fit_reg=fit_reg, label=label, color=color)
    if lp:
        sns.regplot(data=df_proj, x='fix_year', y='lp_lifetime', x_estimator=estimator, x_ci=None, marker='^', color='darkseagreen', truncate=False, fit_reg=False, label='Li&Paxson estimate')
    ax.set_ylabel('lifetime in days')
    ax.set_xlabel('year of fixing commit')
    ax.set_ylim(ylim)
    if  xlim:
        ax.set_xlim((2007.5, 2020.5))
    if df_proj.fix_year.min() > 2008 & lw > 0:
        ax.axvline(0, color='grey', lw=8, alpha=0.6, label='Insufficient data')
        ax.axvline(2007.5, color='grey', lw=lw, alpha=0.6)
    
    plt.legend()
    if stats:
        X = sorted(list(df_proj.fix_year.unique()))
        X_ = sm.add_constant(X)
        y = [estimator(df_proj.loc[df_proj.fix_year == x][field]) for x in X]
        model = sm.OLS(y,X_).fit()
        print(model.summary())
        if latex:
            print(model.summary().tables[1].as_latex_tabular())
    return ax

def plot_hist_trend_aggregated(project, estimator=np.mean, stats = False, min=1900, max=2021, data=df, field='lifetime', color='b', debug=False, latex=False):
    if project is None:
        df_proj = data
    else:
        df_proj = data.loc[data.project == project] 
        
    #df_proj = df_proj.loc[df_proj.fix_year >= min].loc[df_proj.fix_year <= max]
    if debug:
        df_counts = df_proj[['fix_year', field]].groupby(by='fix_year').count()
        print(df_counts)
        
    df_proj = df_proj.loc[df_proj.fix_year >= min].loc[df_proj.fix_year <= max]
    bins = calculate_grouping_bins(data=df_proj, field=field, min_year=min, max_year=max)
    if bins is None:
        return None
    df_proj['group_year'] = df_proj.fix_year.apply(lambda x: bins.loc[(bins.year_from < x) & (bins.year_to >= x)]['year_from'].min())
    
    ax = sns.pointplot(data=df_proj, x='group_year', y=field, estimator=estimator, color=color)
    ax.set_xticklabels(bins['label'])
    if stats:
        X = sorted(list(df_proj.group_year.unique()))
        X_ = sm.add_constant(X)
        y = [estimator(df_proj.loc[df_proj.group_year == x][field]) for x in X]
        model = sm.OLS(y,X_).fit()
        print(model.summary())
        if latex:
            print(model.summary().tables[1].as_latex_tabular())
    return ax

def plot_code_age(data=df, project=None, plot_vul_lifetime=True, estimator=np.mean, aggregate=False, debug=False, min_year=1900, max_year = 2099, splits=None, latex=False):
    f = plt.figure()
    f.set_figwidth(6)
    f.set_figheight(3)
    if project is None:
        df_proj = df_code_age
    else:
        df_proj = df_code_age.loc[project].to_frame('age').dropna()
    if plot_vul_lifetime:
        df_vul = data.loc[data.project == project]
        if debug:
            df_counts = df_vul[['fix_year', 'lifetime']].groupby(by='fix_year').count()
            print(df_counts)
        if aggregate:
            
            
            bins = calculate_grouping_bins(df_vul, min_year=min_year, max_year = max_year)
            df_vul['group_year'] = df_vul.fix_year.apply(lambda x: bins.loc[(bins.year_from < x) & (bins.year_to >= x)]['year_from'].min())
            for it, item  in enumerate(bins.iterrows()):
                index, row = item
                data_vul = df_vul.loc[df_vul.group_year == row.year_from]
                val = np.mean(data_vul.lifetime)
                if it == 0:
                    plt.plot([row.year_from, row.year_to], [val, val], color='b', linewidth=3, label='Vul lifetime')
                else: 
                    plt.plot([row.year_from, row.year_to], [val, val], color='b', linewidth=3)

            plt.legend()
        else:
            plot_hist_trend_complete(data=data, project=project, stats=False, fit_reg=True, lp=False, estimator=estimator, xlim=False, ylim=(0,4200), ci=None, latex=latex)
    
     
    df_proj['year'] = df_proj.index
    if splits:
        for split in splits:
            df_proj_split = df_proj.loc[df_proj.year >= split[0]].loc[df_proj.year <= split[1]]
            ax = sns.regplot(data=df_proj_split, x='year', y='age', x_estimator=estimator, x_ci=None, marker='s', truncate=True, label='Regular code age', color='orchid')
    else:
        ax = sns.regplot(data=df_proj, x='year', y='age', x_estimator=estimator, x_ci=None, marker='s', truncate=False, label='Regular code age', color='orchid')
    ax.set_ylabel('lifetime in days')
    ax.set_xlabel('year of fixing commit')
    ax.set_ylim((0,4200))
    plt.legend()
    return ax
    
def plot_lifetime_distribution(project, fit=False, test=False, data=df, field='lifetime', bins=100, color='b', f=True):
    if f:
        f = plt.figure()
        f.set_figwidth(6)
        f.set_figheight(3)
    if project is None:
        df_proj = data
    else:
        df_proj = data.loc[data.project == project]
    a, b = stats.expon.fit(df_proj[field])
    if test:
        print(f'Distribution parameters: {a}, {b}')
    x = np.arange(0, df_proj.lifetime.max(), 10)
    y =  stats.expon.pdf(x, a, b)
    if fit:
        sns.lineplot(x=x, y=y, label='Exponential fit', color=color)
    ax = sns.histplot(data=df_proj, x=field, bins=bins, stat='density', cumulative=False, color=color)
    ax.set_xlim((0, df_proj.lifetime.max()))
    
    mean = np.mean(df_proj[field])
    median = np.median(df_proj[field])
    for p in ax.patches:
        if p.xy[0]< mean and mean <= p.xy[0]+p.get_width():
            p.set_color('tab:red')
            plt.axvline(-100, color='tab:red', lw=1.5, label='Mean')
            height = stats.expon.pdf([p.xy[0]+0.5*p.get_width()], a, b)
            p.set_height(height[0])
        if p.xy[0]< median and median <= p.xy[0]+p.get_width():
            p.set_color('tab:orange')
            plt.axvline(-100, color='tab:orange', lw=1.5, label='Median')
            height = stats.expon.pdf([p.xy[0]+0.5*p.get_width()], a, b)
            p.set_height(height[0])
    plt.legend()
    if test:
        print(stats.kstest(df_proj[field], stats.expon.cdf, [a, b]))
        y = stats.expon.rvs(a, b, size=4700).astype(int)
        print(epps(data[field], y))
       
    return ax

def generate_lifetime_table(field, include_summary=False, fieldname=None, data=df, lifetime_field='lifetime'):
    if fieldname is None:
        fieldname = field
    field_avgs = pd.DataFrame(columns=[fieldname, 'Average', 'Median', 'Std. Deviation', 'Covariance'])
    for field_val in data[field].unique():
        if pd.isnull(field_val):
            continue
        df_field = data.loc[data[field] == field_val]
        field_avgs = field_avgs.append({fieldname: field_val, 'Average': np.mean(df_field[lifetime_field]), 'Median': np.median(df_field[lifetime_field])
                            , 'Std. Deviation': np.std(df_field[lifetime_field]), 'Covariance': np.cov(df_field[lifetime_field])}, ignore_index=True)
    if include_summary:
        field_avgs = field_avgs.append({fieldname: 'Macro Avg.', 'Average': np.mean(field_avgs.Average), 'Median': np.mean(field_avgs.Median)
                            , 'Std. Deviation': np.mean(field_avgs['Std. Deviation']), 'Covariance': np.mean(field_avgs['Covariance'])}, ignore_index=True)
        field_avgs = field_avgs.append({fieldname: 'Overall', 'Average': np.mean(data[lifetime_field]), 'Median': np.median(data[lifetime_field])
                            , 'Std. Deviation': np.std(data[lifetime_field]), 'Covariance': np.cov(data[lifetime_field])}, ignore_index=True)
    field_avgs.set_index(fieldname, inplace=True)
    return field_avgs

def top_cat_samples(data=df, field='lifetime'):
    s_1 = data.loc[data.cat == 1][field]
    s_2 = data.loc[data.cat == 2][field]
    s_3 = data.loc[data.cat == 3][field]
    s_4 = data.loc[data.cat == 4][field]
    s_5 = data.loc[data.cat == 5][field]
    s_6 = data.loc[data.cat == 6][field]
    return s_1, s_2, s_3, s_4, s_5, s_6

def calculate_grouping_bins(data=df, field='lifetime', min_year=0, max_year=2099):
    data = data.loc[data.fix_year >= min_year].loc[data.fix_year <= max_year]
    df_counts = data[['fix_year', field]].groupby(by='fix_year').count()
    bins = df_counts.shape[0]
    while bins > 1:
        df_group = pd.DataFrame(columns=['year_from', 'year_to', 'count', 'label'])
        _, x = pd.cut(df_counts.index, bins=bins, retbins = True)
        min = x[0]
        for max in x[1:]:
            df_group = df_group.append({'year_from': min, 'year_to' :max
                                        , 'count': df_counts.loc[(df_counts.index > min) & (df_counts.index <= max)][field].sum(),
                                        'label': f'{floor(min+1)}-{floor(max)}'}
                                       , ignore_index =True)
            min = max     
        if(df_group['count'].min() >= MIN_SAMPLE_SIZE):
            break
        bins -= 1
        
    if(df_group['count'].min() >= MIN_SAMPLE_SIZE):
        return df_group
    else:
        warnings.warn('Not enough data to group!')
        return None
def pairwise_permutation(values, num_rounds=100000, seed=42, detail=False, sig_level=0.05, bonf_corr = True):
    p_values = []
    for cat_1, value_1 in enumerate(values, start=1):
        try:
            name_1 = list(df.loc[df.cat == cat_1].cat_name)[0]
        except:
            name_1 = str(cat_1)
        for cat_2, value_2 in enumerate(values[cat_1:], start=cat_1 +1):
            try:
                name_2 =  list(df.loc[df.cat == cat_2].cat_name)[0]
            except:
                name_2 = str(cat_2)
            p_value = permutation_test(value_1, value_2, method='approximate',
                           num_rounds=num_rounds,
                           seed=seed)
            if detail:
                print(f'{f"{p_value:0.4f}":<10} {name_1:<45} {name_2:<30}')
            p_values.append(p_value)
    p_values = np.array(p_values)
    if bonf_corr:
        sig = np.count_nonzero(p_values < sig_level/len(p_values))
    else:
        sig = np.count_nonzero(p_values < sig_level)
    print(f'{sig}/{p_values.shape[0]}={(sig/p_values.shape[0])*100:<0.2f}% of pairwise comparisons signficiant (α={sig_level*100:<0.1f}%)')

def kl_divergence(data=df, field='lifetime', bins=100):
    n, bins = np.histogram(data[field], bins = bins, density=True)

    x = np.convolve(bins, np.ones(2), 'valid') / 2
    a, b = stats.expon.fit(data[field])
    y_exp = stats.expon.pdf(x, a, b)

    #kl_divergence(y_true, n)
    return -1 * np.sum(np.where((y_exp != 0), y_exp * np.log(n / y_exp), 0))
df
# -

df.loc[df.project == 'chrome'].sort_values(by='c_lifetime', ascending=False).head(n=50)[['project', 'cve', 'h_lifetime', 'c_lifetime']]

df.loc[pd.isna(df.c_lifetime) == False]

# # Per Project Lifetimes

lt = generate_lifetime_table('project', include_summary=True)
lt.to_csv("../out/lifetimes_table.csv")

# # Historic Trends
#
# Minima and Maxima for the analyis result from previous examination of the data. These are the boundaries that ensure the discussed criterion of at least 20 data points.

# ## Overall

plot_hist_trend_complete(None, stats=True, min=2008, fit_reg=True, ci=None, ylim=(0,2500))
plt.savefig('../out/year_trends/year_trend_All.pdf', bbox_inches='tight')

# ## Chrome

plot_hist_trend_complete('chrome', stats=True, latex=True, debug=False, fit_reg=True, lw=102)
plt.savefig('../out/year_trends/year_trend_chrome.pdf', bbox_inches='tight')

# ## Firefox

plot_hist_trend_complete('firefox', stats=True, fit_reg=True, latex=False)
plt.savefig('../out/year_trends/year_trend_firefox.pdf', bbox_inches='tight', lw=100)

# ## Linux

plot_hist_trend_complete('kernel', stats=True, lw=157, fit_reg=True, latex=False)
plt.savefig('../out/year_trends/year_trend_kernel.pdf', bbox_inches='tight', lw=100)

# ## Wireshark

plot_hist_trend_complete('wireshark', stats=True, latex=False)

# ## Httpd

plot_hist_trend_aggregated('httpd', stats=True, latex=True)

# ## Openssl 

plot_hist_trend_aggregated('openssl', stats=False, debug=True, latex=False, min=2006, max=2020)

# ## PHP

plot_hist_trend_aggregated('php', stats=False, latex=False)

# ## Postgres

plot_hist_trend_aggregated('postgres', stats=False, latex=False)

# ## Qemu

plot_hist_trend_aggregated('qemu', stats=True, latex=False, min=2014, max=2020)

# ## TcpDump

plot_hist_trend_aggregated('tcpdump', stats=False)

# ## Wireshark

plot_hist_trend_aggregated('wireshark', stats=False)

# # Lifetime Distribution

from fitter import Fitter
f = Fitter(df.lifetime)
f.fit()

f.summary()

ax = plot_lifetime_distribution(project=None, fit=True, test=True, bins=200)
print(f'Bin-width: {ax.patches[0].get_width()}')
plt.savefig('../out/distributions/distribution_All_pdf.pdf', bbox_inches='tight', lw=100)
kl_divergence(data=df.loc[df.lifetime < 6100])
mean = np.mean(df.lifetime)
print(f'{df.loc[df.lifetime < mean].shape[0] / df.shape[0] *100 :0.2f}% of vulnerabilities are fixed before the average of {mean:0.2f} days')

# ## QQPlot

loc, scale = stats.expon.fit(df.lifetime)
h= sm.qqplot(df.lifetime, stats.expon, loc=loc, scale=scale, line='45', markerfacecolor='b')
h.axes[0].set_xlim([0, 6500])
h.axes[0].set_ylim([0, 6500])
h.axes[0].set_xlabel('Exponential theoretical quantiles')
h.axes[0].set_ylabel('Sample quantiles')
plt.savefig('../out/distributions/qq_plot.pdf', bbox_inches='tight')

cutoff= 5000
data = df.loc[df.lifetime > 0]
print(f'Data: Percentage of vuls over {cutoff} {data.loc[data.lifetime > cutoff].shape[0] / data.shape[0]: 0.4f}')
a, b = stats.expon.fit(data.lifetime)
print(f'Theoretical: Percentage of vuls over {cutoff}  {1-stats.expon.cdf(cutoff, a, b):0.4f}')

# +
import powerlaw
results = powerlaw.Fit(df.lifetime.to_list(), xmin=0.1)
print(f"Exponential vs power_law: {results.distribution_compare('exponential', 'power_law')}")
print(f"Exponential vs lognormal: {results.distribution_compare('exponential', 'lognormal')}")
print(f"Exponential vs truncated_power_law: {results.distribution_compare('exponential', 'truncated_power_law')}")
print(f"Exponential vs lognormal_positive: {results.distribution_compare('exponential', 'lognormal_positive')}")    
print()
print(results.distribution_compare('stretched_exponential', 'exponential'))
print()
print(results.distribution_compare('stretched_exponential', 'lognormal'))
print(results.distribution_compare('stretched_exponential', 'lognormal_positive'))
print(results.distribution_compare('stretched_exponential', 'power_law'))
print(results.distribution_compare('stretched_exponential', 'truncated_power_law'))

print(f'Stretching factor: {results.stretched_exponential.beta}')



#ax = sns.histplot(data=df, x='lifetime', bins=200, stat='density', cumulative=False, color='b')
ax = results.plot_pdf(label='Data density')
ax = results.exponential.plot_pdf(ax=ax, label='Exp')
plt.legend()

plt.figure()
ax = results.plot_ccdf(label='Data density')
ax = results.stretched_exponential.plot_ccdf(label='Stretched', ax=ax)
ax = results.exponential.plot_ccdf(ax=ax, label='Exp')
plt.legend()
# -

# ## Empirical vs Theoretical values

# +
import math
data = df.loc[df.lifetime > 0]
a, b = stats.expon.fit(data.lifetime)
q = 0.1
for i in range(2, 11):
    cutoff = np.quantile(data.lifetime, q)
    print(f'{f"{q:0.1f}":<4} {f"{cutoff:0.0f}":<10} {f"{stats.expon.cdf(cutoff, a, b):0.4f}":<10} {f"{data.loc[data.lifetime <= cutoff].shape[0] /data.shape[0]:0.4f}":<10}')
    q = i * 0.1

print()
q = 0.95
cutoff = np.quantile(data.lifetime, q)
print(f'{f"{q:0.2f}":<4} {f"{cutoff:0.0f}":<10} {f"{stats.expon.cdf(cutoff, a, b):0.4f}":<10} {f"{data.loc[data.lifetime <= cutoff].shape[0] /data.shape[0]:0.4f}":<10}')

q = 0.99
cutoff = np.quantile(data.lifetime, q)
print(f'{f"{q:0.2f}":<4} {f"{cutoff:0.0f}":<10} {f"{stats.expon.cdf(cutoff, a, b):0.4f}":<10} {f"{data.loc[data.lifetime <= cutoff].shape[0] /data.shape[0]:0.4f}":<10}')

# -

# ## Lifetime Distributions per project

# ### Firefox

plot_lifetime_distribution(project='firefox', fit=True, test=False)
plt.savefig('../out/distributions/distribution_firefox_pdf.pdf', bbox_inches='tight', lw=100)

# ### Chrome

plot_lifetime_distribution(project='chrome', fit=True, test=False)
plt.savefig('../out/distributions/distribution_chrome_pdf.pdf', bbox_inches='tight', lw=100)

# ### Linux

plot_lifetime_distribution(project='kernel', fit=True, test=False)
plt.savefig('../out/distributions/distribution_linux_pdf.pdf', bbox_inches='tight', lw=100)

# ## Wireshark

plot_lifetime_distribution(project='wireshark', fit=True, test=True, bins=50)
plt.savefig('../out/distributions/distribution_wireshark_pdf.pdf', bbox_inches='tight', lw=100)

# ## Historic Development of distribution

cutoffs = [2013, 2015, 2017, 2020]
prev_year = 0
for year in cutoffs:
    data = df.loc[df.fix_year > prev_year].loc[df.fix_year <=year]
    a, b = stats.expon.fit(data.lifetime)
    x = np.arange(0, df.lifetime.max(), 10)
    y =  stats.expon.pdf(x, a, b)
    sns.lineplot(x=x, y=y, label=f'Exponential fit <= {year}')
plt.savefig('../out/distributions/distribution_All_split_4_pdf.pdf', bbox_inches='tight')

# # Vulnerabiltiy types

s1, s2, s3, s4, s5, s6 = top_cat_samples()
print(stats.kruskal(s1, s2, s3, s4, s5, s6))
generate_lifetime_table('cat_name', include_summary=False)
#df_temp = generate_lifetime_table('cat_name', include_summary=False)[ 'Average']
#df_temp.to_latex()
#pairwise_permutation([s1, s2, s3, s4, s5, s6], num_rounds=10000, detail=True, bonf_corr=True)

# ## Chrome

s1, s2, s3, s4, s5, s6 = top_cat_samples(df.loc[df.project == 'chrome'])
print(stats.kruskal(s1, s2, s3, s4, s5, s6))
generate_lifetime_table('cat_name', include_summary=False, data=df.loc[df.project == 'chrome'])
#df_temp = generate_lifetime_table('cat_name', include_summary=False, data=df.loc[df.project == 'chrome'])[ 'Average']
#df_temp.to_latex()

# ## Firefox

s1, s2, s3, s4, s5, s6 = top_cat_samples(df.loc[df.project == 'firefox'])
print(stats.kruskal(s1, s2, s3, s4, s5, s6))
generate_lifetime_table('cat_name', include_summary=False, data=df.loc[df.project == 'firefox'])

# ## Linux

s1, s2, s3, s4, s5, s6 = top_cat_samples(df.loc[df.project == 'kernel'])
print(stats.kruskal(s1, s2, s3, s4, s5, s6))
generate_lifetime_table('cat_name', include_summary=False, data=df.loc[df.project == 'kernel'])

# ## Comparison against Li&Paxson
#
# To confirm these results we show that we would arrive at the same conclusion using the lower bound approach of Li&Paxson. (Note: This lowerbound is not identical to the one proposed by Li&Paxson but instead the equivalent of considering the newest blamed VCC candidate from our heuristic)

s1, s2, s3, s4, s5, s6 = top_cat_samples(field='lp_lifetime')
print(stats.kruskal(s1, s2, s3, s4, s5, s6))
generate_lifetime_table('cat_name', include_summary=False, lifetime_field='lp_lifetime')

# Again only looking at the statistics over all the projects we would confidently reject the Null-hypothesis that the categories follow the same distribution. Thus, arriving at the conclusion that there is a significant difference in lifetime between categories

print('\033[1mChrome:\n\033[0m')
s1, s2, s3, s4, s5, s6 = top_cat_samples(df.loc[df.project == 'chrome'], field='lp_lifetime')
print(stats.kruskal(s1, s2, s3, s4, s5, s6))
print('')
print('\033[1mFirefox:\n\033[0m')
s1, s2, s3, s4, s5, s6 = top_cat_samples(df.loc[df.project == 'firefox'], field='lp_lifetime')
print(stats.kruskal(s1, s2, s3, s4, s5, s6))
pairwise_permutation([s1, s2, s3, s4, s5, s6], num_rounds=1000, detail=True)
print('')
print('\033[1mLinux kernel:\n\033[0m')
s1, s2, s3, s4, s5, s6 = top_cat_samples(df.loc[df.project == 'kernel'], field='lp_lifetime')
print(stats.kruskal(s1, s2, s3, s4, s5, s6))

# ## Comparison of lifetimetrends

# ### Memory issues

# +
#df_kernel = df.loc[df.project == 'kernel']

df_mem = df.loc[df.cat == 1]
print(len(df_mem)/len(df))
plot_hist_trend_complete(project=None, data=df_mem, lp=None, ci=None, xlim=None, debug=False, color='r', label='Memory vulnerabilities', max=2020, fit_reg=True)
df_others = df.loc[df.cat != 1]
print(len(df_others)/len(df))
plot_hist_trend_complete(project=None, data=df_others, lp=None, ci=None, xlim=None, debug=False, min=2010, color='g', f=False, label='Others', max=2020, fit_reg=True, marker='+')
plt.savefig('../out/year_trends/year_trend_all_mem_vs_others.pdf', bbox_inches='tight')
# -

# ## Kernel

MIN_SAMPLE_SIZE_2 = 20
df_kernel = df.loc[df.project == 'kernel']
df_mem = df_kernel.loc[df_kernel.cat == 1]
print(len(df_mem)/len(df_kernel))
plot_hist_trend_complete(debug=False, project=None, data=df_mem, lp=None, ci=None, xlim=None, color='r', label='Memory vulnerabilities', max=2020, fit_reg=True, ylim=[0, 2800])
df_others = df_kernel.loc[df_kernel.cat != 1]
print(len(df_others)/len(df_kernel))
ax = plot_hist_trend_complete(project=None, data=df_others, lp=None, ci=None, xlim=None, debug=False, color='g', f=False, label='Others', max=2020, fit_reg=True, marker='+', ylim=None)
ax.set_xticks(range(2011, 2021))
MIN_SAMPLE_SIZE_2 = 45
plt.savefig('../out/year_trends/year_trend_kernel_mem_vs_others.pdf', bbox_inches='tight')

# ## Chrome

MIN_SAMPLE_SIZE_2 = 20
df_chrome = df.loc[df.project == 'chrome']
df_mem = df_chrome.loc[df_chrome.cat == 1]
print(len(df_mem)/len(df_chrome))
plot_hist_trend_complete(debug=False, project=None, data=df_mem, lp=None, ci=None, xlim=None, color='r', label='Memory vulnerabilities', max=2020, fit_reg=True, ylim=None)
df_others = df_chrome.loc[df_chrome.cat != 1]
print(len(df_others)/len(df_chrome))
plot_hist_trend_complete(project=None, data=df_others, lp=None, ci=None, xlim=None, debug=False, color='g', f=False, label='Others', min=2011, max=2020, fit_reg=True, marker='+', ylim=[0, 1200])
MIN_SAMPLE_SIZE_2 = 45
plt.savefig('../out/year_trends/year_trend_chrome_mem_vs_others.pdf', bbox_inches='tight')

# ## Firefox

MIN_SAMPLE_SIZE_2 = 20
df_firefox = df.loc[df.project == 'firefox']
df_mem = df_firefox.loc[df_firefox.cat == 1]
print(len(df_mem)/len(df_firefox))
plot_hist_trend_complete(debug=False, project=None, data=df_mem, lp=None, ci=None, xlim=None, color='r', label='Memory vulnerabilities',min=2012, max=2020, fit_reg=True, ylim=[0, 1950])
df_others = df_firefox.loc[df_firefox.cat != 1]
print(len(df_others)/len(df_firefox))
plot_hist_trend_complete(project=None, data=df_others, lp=None, ci=None, xlim=None, debug=False, color='g', f=False, label='Others', min=2012, max=2020, fit_reg=True, marker='+', ylim=None)
MIN_SAMPLE_SIZE_2 = 45
plt.savefig('../out/year_trends/year_trend_firefox_mem_vs_others.pdf', bbox_inches='tight')

# ## Others

df_others = df.loc[df.cat != 1]
plot_hist_trend_complete(project=None, data=df_others)

# The results for Chrome and the Linux Kernel support the hypothesis that differences in lifetime between categories are the result of an underlying in difference of categories per project.

# # Result comparision against ground truth
# In the final remarks from the reviewers we were asked to conduct the experiments regarding 
#  - average lifetime trend
#  - distribution of lifetimes per year
#
# on the ground truth only and compare these results to the conclusions made on the entire dataset

# ## Average lifetime trend

df_gt = df.loc[(df.c_lifetime.isna() == False)]
#df_gt = df.loc[(df.c_lifetime.isna() == False) ]
print(df_gt.shape[0])
plot_hist_trend_complete(None, stats=False, min=2010, max=2019,  data=df_gt, field='c_lifetime', color='tab:orange')
plot_hist_trend_complete(None, stats=False, min=2010, max=2019, data=df_gt, field='h_lifetime')


# ## Kernel

MIN_SAMPLE_SIZE_2 = 35
df_gt_kernel = df.loc[(df.c_lifetime.isna() == False) & (df.project == 'kernel')]
plot_hist_trend_complete(None, debug=True, stats=True, data=df_gt_kernel, field='h_lifetime', xlim=None, fit_reg=True, lp=False, label='Heuristic Lifetime', ci=None)
ax = plot_hist_trend_complete(None, stats=True, data=df_gt_kernel, field='c_lifetime', xlim=None, fit_reg=True, lp=False, label='Groundtruth lifetime', color='coral', f=False, marker='D', ci=None)
ax.set_xticks(range(2011, 2021))
plt.savefig('../out/year_trends/year_trend_linux_gt_comp.pdf', bbox_inches='tight')
MIN_SAMPLE_SIZE_2 = 45

# ## Chrome

# +
df_gt_chrome = df.loc[(df.c_lifetime.isna() == False) & (df.project == 'chrome')]
MIN_SAMPLE_SIZE_2 = 20
plot_hist_trend_complete(None, stats=True, data=df_gt_chrome, field='c_lifetime', xlim=None, fit_reg=True, lp=False, label='Groundtruth lifetime', color='coral',  marker='D', ci=None)
plot_hist_trend_complete(None, debug=True, stats=True, data=df_gt_chrome, field='h_lifetime', xlim=None, fit_reg=True, lp=False, label='Heuristic Lifetime', f=False, ci=None)

plt.savefig('../out/year_trends/year_trend_chrome_gt_comp.pdf', bbox_inches='tight')
MIN_SAMPLE_SIZE_2 = 20
# -

# ## Httpd

df_gt_httpd = df.loc[(df.c_lifetime.isna() == False) & (df.project == 'httpd')]
plot_hist_trend_aggregated(None, stats=False, data=df_gt_httpd, field='h_lifetime')
plot_hist_trend_aggregated(None, stats=False, data=df_gt_httpd, field='c_lifetime', color='tab:orange')

# ## Lifetime Distribution

df_gt = df.loc[(df.c_lifetime.isna() == False)]
ax = plot_lifetime_distribution(project=None, fit=True, test=True, field='h_lifetime', data=df_gt, bins=100, color='b')
ax.set_xlabel('Heuristic lifetime (days)')
#plt.figure()
plt.savefig('../out/distributions/distribution_gtdata_heuristic.pdf', bbox_inches='tight')
ax = plot_lifetime_distribution(project=None, fit=True, test=True, field='c_lifetime', data=df_gt, bins=100, color='coral')
ax.set_xlabel('Ground truth lifetime (days)')
plt.savefig('../out/distributions/distribution_gtdata_gt.pdf', bbox_inches='tight')


# +
df_gt = df.loc[(df.c_lifetime.isna() == False)]
loc, scale = stats.expon.fit(df_gt.h_lifetime)
h= sm.qqplot(df_gt.h_lifetime, stats.expon, loc=loc, scale=scale, line='45', markerfacecolor='b')
h.axes[0].set_xlim([0, 6500])
h.axes[0].set_ylim([0, 6500])
h.axes[0].set_xlabel('Exponential theoretical quantiles')
h.axes[0].set_ylabel('Heuristic sample quantiles')
plt.savefig('../out/distributions/qqplot_gtdata_heuristic.pdf', bbox_inches='tight')

loc, scale = stats.expon.fit(df_gt.c_lifetime)
gt = sm.qqplot(df_gt.c_lifetime, stats.expon, loc=loc, scale=scale, line='45', markerfacecolor='coral', color='coral')
gt.axes[0].set_xlim([0, 6500])
gt.axes[0].set_ylim([0, 6500])
gt.axes[0].set_xlabel('Exponential theoretical quantiles')
gt.axes[0].set_ylabel('Groundtruth sample quantiles')
plt.savefig('../out/distributions/qqplot_gtdata_gt.pdf', bbox_inches='tight')

# +
cutoffs = [2013, 2015, 2017, 2020]
prev_year = 0
df_gt = df.loc[pd.isna(df.c_lifetime) == False]
f = plt.figure()
f.set_figwidth(6)
f.set_figheight(3.5)
for year in cutoffs:
    data = df_gt.loc[df_gt.fix_year > prev_year].loc[df_gt.fix_year <=year]
    a, b = stats.expon.fit(data.h_lifetime)
    a = 0
    x = np.arange(0, df.lifetime.max(), 10)
    y =  stats.expon.pdf(x, a, b)
    ax= sns.lineplot(x=x, y=y, label=f'Exponential fit <= {year}')

ax.set_ylim([0, 0.0015])
ax.set_ylabel('Density')
ax.set_xlabel('Heuristic lifetime (days)')
plt.savefig('../out/distributions/distribution_all_split_4_gt_heuristic.pdf', bbox_inches='tight')
f = plt.figure()
f.set_figwidth(6)
f.set_figheight(3.5)

prev_year = 0
for year in cutoffs:
    data = df_gt.loc[df_gt.fix_year > prev_year].loc[df_gt.fix_year <=year]
    a, b = stats.expon.fit(data.c_lifetime)
    x = np.arange(0, df.lifetime.max(), 10)
    y =  stats.expon.pdf(x, a, b)
    ax = sns.lineplot(x=x, y=y, label=f'Exponential fit <= {year}')
    ax.set_ylim([0, 0.0015])
plt.savefig('../out/distributions/distribution_all_split_4_gt_gt.pdf', bbox_inches='tight')
ax.set_ylim([0, 0.0015])
ax.set_ylabel('Density')
ax.set_xlabel('Groundtruth lifetime (days)')
# -

# # Regular Code age

# ## Firefox

plot_code_age(project='firefox')
plt.savefig('../out/regular_code_age/year_trend_firefox_with_regular.pdf', bbox_inches='tight')

# ## Chrome

plot_code_age(project='chrome')
plt.savefig('../out/regular_code_age/year_trend_chrome_with_regular.pdf', bbox_inches='tight')

# ## Linux

plot_code_age(project='kernel')
plt.savefig('../out/regular_code_age/year_trend_kernel_with_regular.pdf', bbox_inches='tight')

# ## Httpd

ax = plot_code_age(project='httpd', aggregate=True)
ax.set_xticks(range(2000, 2019, 2))
plt.savefig('../out/regular_code_age/year_trend_httpd_with_regular.pdf', bbox_inches='tight')

# ## PHP

ax = plot_code_age(project='php', aggregate=True)
ax.set_xticks(range(2002, 2021, 2))
plt.savefig('../out/regular_code_age/year_trend_regular_php.pdf', bbox_inches='tight')

# ## Qemu

ax = plot_code_age(project='qemu', aggregate=True, debug=True, min_year=2014, max_year=2020)
ax.set_xlim(2013.5, 2020.5)
plt.savefig('../out/regular_code_age/year_trend_qemu_with_regular.pdf', bbox_inches='tight')

# ## ffmpeg

ax = plot_code_age(project='ffmpeg', aggregate=True)
plt.savefig('../out/regular_code_age/year_trend_regular_ffmpeg.pdf', bbox_inches='tight')

# ## OpenSSL

ax = plot_code_age(project='openssl', aggregate=True, debug=False, min_year=2006, max_year=2020, splits=[[2006, 2014], [2016, 2020]])
df_proj = df_code_age.loc['openssl']
df_proj['year'] = df_proj.index
print(df_proj[2015])
plt.plot([2015,], [df_proj[2015],], marker='s', color='orchid', markersize=7)
plt.savefig('../out/regular_code_age/year_trend_openssl_with_regular.pdf', bbox_inches='tight')


# ## Wireshark

MIN_SAMPLE_SIZE_2 = 20
ax = plot_code_age(project='wireshark', aggregate=False, debug=True)
ax.set_xlim(2013.75, 2019.25)
plt.savefig('../out/regular_code_age/year_trend_wireshark_with_regular.pdf', bbox_inches='tight')
MIN_SAMPLE_SIZE_2 = 45

# ## Postgres

ax = plot_code_age(project='postgres', aggregate=True)
plt.savefig('../out/regular_code_age/year_trend_regular_postgres.pdf', bbox_inches='tight')

proj = 'kernel'
df_proj = df_code_age.loc[proj].to_frame('age').dropna()
df_proj['year'] = df_proj.index
sns.pointplot(data=df_proj, x='year', y='age')
plot_hist_trend_complete(proj)

df.groupby(by='cat_name').count()
