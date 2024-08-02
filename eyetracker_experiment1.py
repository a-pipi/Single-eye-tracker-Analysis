#%%
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats
# %matplotlib qt

from helpers.recording_state import RecordingState
from helpers.calculate_rms_s2s import calculate_rms_s2s
from helpers.calculate_sd_2d_array import calculate_sd_2d_array
from helpers.calculate_bcea import calculate_bcea
from helpers.check_normality import check_normality
from helpers.vergence_target import vergence_target
from helpers.convert_degrees_2_mm import convert_degrees_2_mm

# set subject IDs
subject_IDs = ['s001',
               's003',
               's004',
               's005',
               's006',
               's007',]

# set parameters
procedures = [RecordingState.MEASUREMENT.name,
              RecordingState.MEASUREMENT_LEFT.name,
              RecordingState.MEASUREMENT_RIGHT.name,]

figures_dir = 'figures'
check_normality_flag = False

procedure = procedures[0]
subject_ID = subject_IDs[0]
# iterate over all stimuli
mean_pogx_subject = np.array([])
mean_pogy_subject = np.array([])
stim_posx_subject = np.array([])
stim_posy_subject = np.array([])
stimulus_ids = np.array([])
subject_ids = np.array([])
procedure_ids = np.array([])
outliers = np.array([])
viewing = np.array([])
eye_id = np.array([])
precision_x_SDs = np.array([])
precision_y_SDs = np.array([])
precision_R_SDs = np.array([])
precision_x_S2Ss = np.array([])
precision_y_S2Ss = np.array([])
precision_R_S2Ss = np.array([])
ae_x = np.array([])
ae_y = np.array([])
vae = np.array([]) # Vecotrial amplitude, in oculomotor literatuur wordt dit vaak R genoemd
ae_vergences = np.array([])

for procedure in procedures:
    stimulus_numbers = np.linspace(1,35,35)

    if procedure == RecordingState.MEASUREMENT.name:
        eyes = ['left', 'right']
        ocular = 'binocular'
        print('kom ik hier')
    if procedure == RecordingState.MEASUREMENT_LEFT.name:
        eyes = ['left']
        ocular = 'monocular'
    if procedure == RecordingState.MEASUREMENT_RIGHT.name:
        eyes = ['right']
        ocular = 'monocular'

    for eye in eyes:
        print(f'{eye}_pog_degrees | {procedure} | {eyes}')
        for subject_ID in subject_IDs:
            # load data
            loaded_data = np.load(f'data/{subject_ID}/analysis data/data_{procedure.lower()}.npz')
            pog_degrees = loaded_data[f'{eye}_pog_degrees']
            time = loaded_data['time']
            is_outlier = loaded_data['is_outlier']
            stim_degrees = loaded_data['stim_pos_degrees']
            stimulus_number = loaded_data['stimulus_number']

            for stimulus in stimulus_numbers:
                stimulus_indices = np.where(stimulus_number == stimulus)[0]

                mean_pog_deg = np.nanmean(pog_degrees[stimulus_indices,:2], axis=0)
                # precision_SD = np.nanstd(pog_degrees[stimulus_indices,:2], axis=0)
                # precision_R_SD = calculate_sd_2d_array(pog_degrees[stimulus_indices,:2])
                bcea, sigma_x, sigma_y = calculate_bcea(pog_degrees[stimulus_indices,:2])
                precision_S2S = calculate_rms_s2s(pog_degrees[stimulus_indices,:2])
                stim_pos_deg = stim_degrees[stimulus_indices[0]]
                outlier = is_outlier[stimulus_indices[0]]
                ae = np.abs(mean_pog_deg-stim_pos_deg)
                vectorial_ae = np.linalg.norm(mean_pog_deg-stim_pos_deg)

                ae_vergence = np.nan
                if procedure == RecordingState.MEASUREMENT.name:
                    # load vergence specific data
                    left_visual_axis = loaded_data['left_visual_axis']
                    right_visual_axis = loaded_data['right_visual_axis']
                    left_cor = loaded_data['left_cor']
                    right_cor = loaded_data['right_cor']
                    
                    target = np.append(convert_degrees_2_mm(stim_pos_deg, 650), 0)

                    # calculate target vergence for each stimulus
                    target_vergence = vergence_target(target, left_cor, right_cor)

                    gaze_vergence = np.degrees(np.arccos(np.sum(
                        left_visual_axis[stimulus_indices,:] * right_visual_axis[stimulus_indices,:], 
                        axis=1)))
                    
                    ae_vergence = np.abs(np.mean(gaze_vergence) - target_vergence)


                if not np.isnan(mean_pog_deg[0]) or not np.isnan(mean_pog_deg[1]):
                    mean_pogx_subject = np.append(mean_pogx_subject, mean_pog_deg[0])
                    mean_pogy_subject = np.append(mean_pogy_subject, mean_pog_deg[1])
                    ae_x = np.append(ae_x, ae[0])
                    ae_y = np.append(ae_y, ae[1])
                    vae = np.append(vae, vectorial_ae)
                    precision_x_SDs = np.append(precision_x_SDs, sigma_x)      #precision_SD[0])
                    precision_y_SDs = np.append(precision_y_SDs, sigma_y)  #precision_SD[1])
                    precision_R_SDs = np.append(precision_R_SDs, bcea)  #precision_R_SD)
                    precision_x_S2Ss = np.append(precision_x_S2Ss, precision_S2S[0])
                    precision_y_S2Ss = np.append(precision_y_S2Ss, precision_S2S[1])
                    precision_R_S2Ss = np.append(precision_R_S2Ss, precision_S2S[2])
                    stim_posx_subject = np.append(stim_posx_subject, stim_pos_deg[0])
                    stim_posy_subject = np.append(stim_posy_subject, stim_pos_deg[1])
                    stimulus_ids = np.append(stimulus_ids, stimulus)
                    subject_ids = np.append(subject_ids, subject_ID)
                    procedure_ids = np.append(procedure_ids, procedure)
                    outliers = np.append(outliers, outlier)
                    viewing = np.append(viewing, f'{ocular}')
                    eye_id = np.append(eye_id, f'{eye}')
                    ae_vergences = np.append(ae_vergences, ae_vergence)

data = pd.DataFrame({
    'subject ID': subject_ids,
    'stimulus ID': stimulus_ids,
    'procedure': procedure_ids,
    'pog x': mean_pogx_subject,
    'pog y': mean_pogy_subject,
    'ae x': ae_x,
    'ae y': ae_y,
    'R': vae,
    'precision x SD': precision_x_SDs,
    'precision y SD': precision_y_SDs,
    'precision R SD': precision_R_SDs,
    'precision x S2S': precision_x_S2Ss,
    'precision y S2S': precision_y_S2Ss,
    'precision R S2S': precision_R_S2Ss,
    'stimulus position x': stim_posx_subject,
    'stimulus position y': stim_posy_subject,
    'outlier': outliers,
    'viewing': viewing,
    'eye': eye_id,
    'ae vergence': ae_vergences
})

data_single_subject = data[data['subject ID'] == 's003']
data_stimuli = data_single_subject[data_single_subject['procedure'] == 'MEASUREMENT_RIGHT']
data_no_outliers = data[data['outlier'] == 0]
data_no_outliers_central = data_no_outliers[data_no_outliers['stimulus position x'].between(-15, 15)]

mae_subject = data_no_outliers.groupby(['subject ID', 'viewing', 'eye'])[['ae x', 'ae y', 'R']].mean().reset_index()
mae_subject_central = data_no_outliers_central.groupby(['subject ID', 'viewing', 'eye'])[['ae x', 'ae y', 'R']].mean().reset_index()

sd_subject = data_no_outliers.groupby(['subject ID', 'viewing', 'eye'])[['precision x SD', 'precision y SD', 'precision R SD']].mean().reset_index()
sd_subject_central = data_no_outliers_central.groupby(['subject ID', 'viewing', 'eye'])[['precision x SD', 'precision y SD', 'precision R SD']].mean().reset_index()

s2s_subject = data_no_outliers.groupby(['subject ID', 'viewing', 'eye'])[['precision x S2S', 'precision y S2S', 'precision R S2S']].mean().reset_index()
s2s_subject_central = data_no_outliers_central.groupby(['subject ID', 'viewing', 'eye'])[['precision x S2S', 'precision y S2S', 'precision R S2S']].mean().reset_index()


#%%
# Scatter plot of a single subject
figure1 = plt.figure(figsize=(10, 6))
sns.scatterplot(x='stimulus position x',
                y='stimulus position y',
                data=data_stimuli,
                color='black',
                s=50,
                figure=figure1)
sns.scatterplot(x='pog x',
                y='pog y',
                data=data_single_subject,
                hue='viewing',
                style='viewing',
                figure=figure1)

axis1 = figure1.axes[0]
axis1.set_xlim([-30,30])
axis1.set_ylim([-20,20])

axis1.set_ylabel('Vertical POG ($^\circ$)')
axis1.set_xlabel('Horizontal POG ($^\circ$)')

handles, labels = axis1.get_legend_handles_labels()
new_labels = [label.replace('subject ID', '').strip() for label in labels]
axis1.legend(handles, new_labels, title='', loc='upper left', bbox_to_anchor=(1, 1))

plt.savefig(f'{figures_dir}/single subject pog estimates.png', bbox_inches='tight')

#%%
# horizontal pog vs target 
figure2, axs2 = plt.subplots(1,2, figsize=(10,6))

# draw identity lines
axs2[0].axline((0,0), slope=1, color='gray', zorder=0)
axs2[1].axline((0,0), slope=1, color='gray', zorder=0)

sns.scatterplot(data=data_no_outliers[data_no_outliers['viewing'] == 'monocular'], 
                x='stimulus position x', y='pog x',
                hue='subject ID', style='subject ID', 
                s=100, ax=axs2[0])
sns.scatterplot(data=data_no_outliers[data_no_outliers['viewing'] == 'binocular'], 
                x='stimulus position x', y='pog x',
                hue='subject ID', style='subject ID', 
                s=100, ax=axs2[1])


axs2[0].legend_.remove()
axs2[0].set_xlabel('Horizontal Stimulus Position ($^\circ$)')
axs2[0].set_ylabel('Horizontal POG ($^\circ$)')

axs2[1].legend_.remove()
axs2[1].set_xlabel('Horizontal Stimulus Position ($^\circ$)')
axs2[1].set_ylabel('')

# Defining custom 'xlim' and 'ylim' values.
custom_xlim = (-24, 24)
custom_ylim = (-35, 35)

# Setting the values for all axes.
plt.setp(axs2, xlim=custom_xlim, ylim=custom_ylim)

handles, labels = axs2[1].get_legend_handles_labels()
new_labels = [label.replace('subject ID', '').strip() for label in labels]
axs2[1].legend(handles, new_labels, title='', loc='upper left', bbox_to_anchor=(1, 1))

plt.savefig(f'{figures_dir}/horizontal pog estimates vs target.png', bbox_inches='tight')

#%%
# vertical pog vs target 
figure3, axs3 = plt.subplots(1,2, figsize=(10,6))

# draw identity lines
axs3[0].axline((0,0), slope=1, color='gray', zorder=0)
axs3[1].axline((0,0), slope=1, color='gray', zorder=0)

sns.scatterplot(data=data_no_outliers[data_no_outliers['viewing'] == 'monocular'], 
                x='stimulus position y', y='pog y',
                hue='subject ID', style='subject ID', 
                s=100, ax=axs3[0])
sns.scatterplot(data=data_no_outliers[data_no_outliers['viewing'] == 'binocular'], 
                x='stimulus position y', y='pog y',
                hue='subject ID', style='subject ID', 
                s=100, ax=axs3[1])

axs3[0].legend_.remove()
axs3[0].set_xlabel('Vertical Stimulus Position ($^\circ$)')
axs3[0].set_ylabel('Vertical POG ($^\circ$)')

axs3[1].legend_.remove()
axs3[1].set_xlabel('Vertical Stimulus Position ($^\circ$)')
axs3[1].set_ylabel('')

# Defining custom 'xlim' and 'ylim' values.
custom_xlim = (-12, 12)
custom_ylim = (-25, 25)

# Setting the values for all axes.
plt.setp(axs3, xlim=custom_xlim, ylim=custom_ylim)

handles, labels = axs3[1].get_legend_handles_labels()
new_labels = [label.replace('subject ID', '').strip() for label in labels]
axs3[1].legend(handles, new_labels, title='', loc='upper left', bbox_to_anchor=(1, 1))

plt.savefig(f'{figures_dir}/vertical pog estimates vs target.png', bbox_inches='tight')

#%%
# MAE boxplot
melted_mae_subject = mae_subject.melt(id_vars=['subject ID', 'viewing', 'eye'], value_vars=['ae x', 'ae y', 'R'], 
                    var_name='ae type', value_name='ae value')
melted_mae_subject['ae type'] = melted_mae_subject['ae type'].replace({'ae x': 'x',
                                                                       'ae y': 'y'})

melted_mae_subject_central = mae_subject_central.melt(id_vars=['subject ID', 'viewing', 'eye'], value_vars=['ae x', 'ae y', 'R'], 
                    var_name='ae type', value_name='ae value')
melted_mae_subject_central['ae type'] = melted_mae_subject_central['ae type'].replace({'ae x': 'x',
                                                                       'ae y': 'y'})
# MAE per monocular and binocular with both eye together
figure4, axs4 = plt.subplots(1,2, figsize=(12, 6))
sns.boxplot(x='ae type', y='ae value', hue='viewing', data=melted_mae_subject,
            ax=axs4[0], showfliers=False)
sns.stripplot(x='ae type', y='ae value', hue='viewing', data=melted_mae_subject, 
              dodge=True, alpha=0.7, ax=axs4[0], size=10, 
              edgecolor='white', linewidth=2, legend=False)


axs4[0].set_ylim([0, 4])
axs4[0].set_xlabel('')  
axs4[0].set_ylabel('')
axs4[0].legend_.remove()

sns.boxplot(x='ae type', y='ae value', hue='viewing', data=melted_mae_subject_central,
            ax=axs4[1], showfliers=False)
sns.stripplot(x='ae type', y='ae value', hue='viewing', data=melted_mae_subject_central, 
              dodge=True, alpha=0.7, ax=axs4[1], size=10, 
              edgecolor='white', linewidth=2, legend=False)
axs4[1].set_ylim([0, 4])
axs4[1].set_xlabel('')
axs4[1].set_ylabel('')

# Simplify legend by removing the word "viewing"
handles, labels = axs4[1].get_legend_handles_labels()
new_labels = [label.replace('viewing', '').strip() for label in labels]
axs4[1].legend(handles, new_labels, title='', loc='upper left', bbox_to_anchor=(1, 1))

figure4.align_ylabels()

# Set a shared y-label
figure4.text(0.04, 0.5, 'MAE ($^\circ$)', va='center', rotation='vertical', fontsize=12)

plt.show()

figure4.savefig(f'{figures_dir}/MAE boxplot.png', bbox_inches='tight')

mae_summary = melted_mae_subject.groupby(['viewing', 'ae type'])['ae value'].agg(['mean', 'std']).reset_index().sort_values('viewing')
mae_summary_cenrtal = melted_mae_subject_central.groupby(['viewing', 'ae type'])['ae value'].agg(['mean', 'std']).reset_index().sort_values('viewing')

print('All points:')
print(mae_summary)
print('')
print('Central points:')
print(mae_summary_cenrtal)

# t-tests to test difference between monocular and binocular viewing
# Separate data by viewing condition
binocular_data = mae_subject[mae_subject['viewing'] == 'binocular']
monocular_data = mae_subject[mae_subject['viewing'] == 'monocular']

# Variables to test
variables = ['ae x', 'ae y', 'R']

# Perform t-tests
for var in variables:
    # Extract data for each variable
    binoc_values = binocular_data[var]
    monoc_values = monocular_data[var]

    # Perform independent t-test
    t_stat, p_value = stats.ttest_ind(binoc_values, monoc_values)
    
    # Print results
    print(f'Test for {var}:')
    print(f'  T-statistic: {t_stat:.4f}')
    print(f'  P-value: {p_value:.4f}')
    print()

if check_normality_flag:
    check_normality(mae_subject[mae_subject['viewing'] == 'monocular']['ae x'])
    check_normality(mae_subject[mae_subject['viewing'] == 'monocular']['ae y'])
    check_normality(mae_subject[mae_subject['viewing'] == 'binocular']['ae x'])
    check_normality(mae_subject[mae_subject['viewing'] == 'binocular']['ae y'])


#%%
# precision SD
melted_sd_subject = sd_subject.melt(id_vars=['subject ID', 'viewing', 'eye'], 
                                    value_vars=['precision x SD', 'precision y SD', 'precision R SD'], 
                                    var_name='precision type', value_name='precision value')
melted_sd_subject['precision type'] = melted_sd_subject['precision type'].replace({'precision x SD': 'SD x',
                                                                       'precision y SD': 'SD y',
                                                                       'precision R SD': 'BCEA'})

melted_sd_subject_central = sd_subject_central.melt(id_vars=['subject ID', 'viewing', 'eye'], 
                                                    value_vars=['precision x SD', 'precision y SD', 'precision R SD'], 
                                                    var_name='precision type', value_name='precision value')
melted_sd_subject_central['precision type'] = melted_sd_subject_central['precision type'].replace({'precision x SD': 'SD x',
                                                                       'precision y SD': 'SD y',
                                                                       'precision R SD': 'BCEA'})
# precision per monocular and binocular with both eye together
figure3, axs3 = plt.subplots(1,2, figsize=(12, 6))
sns.boxplot(x='precision type', y='precision value', hue='viewing', data=melted_sd_subject,
            ax=axs3[0], showfliers=False)
sns.stripplot(x='precision type', y='precision value', hue='viewing', data=melted_sd_subject, 
              dodge=True, alpha=0.7, ax=axs3[0], size=10, 
              edgecolor='white', linewidth=2, legend=False)


axs3[0].set_ylim([0, 1])
axs3[0].set_xlabel('')  
axs3[0].set_ylabel('')
axs3[0].legend_.remove()

sns.boxplot(x='precision type', y='precision value', hue='viewing', data=melted_sd_subject_central,
            ax=axs3[1], showfliers=False)
sns.stripplot(x='precision type', y='precision value', hue='viewing', data=melted_sd_subject_central, 
              dodge=True, alpha=0.7, ax=axs3[1], size=10, 
              edgecolor='white', linewidth=2, legend=False)
axs3[1].set_ylim([0, 1])
axs3[1].set_xlabel('')
axs3[1].set_ylabel('')

# Simplify legend by removing the word "viewing"
handles, labels = axs3[1].get_legend_handles_labels()
new_labels = [label.replace('viewing', '').strip() for label in labels]
axs3[1].legend(handles, new_labels, title='', loc='upper left', bbox_to_anchor=(1, 1))

figure3.align_ylabels()

# Set a shared y-label
figure3.text(0.04, 0.5, 'Precision ($^\circ$)', va='center', rotation='vertical', fontsize=12)

plt.show()

figure3.savefig(f'{figures_dir}/SD boxplot.png', bbox_inches='tight')

precision_summary = melted_sd_subject.groupby(['viewing', 'precision type'])['precision value'].agg(['mean', 'std']).reset_index().sort_values('viewing')
precision_summary_cenrtal = melted_sd_subject_central.groupby(['viewing', 'precision type'])['precision value'].agg(['mean', 'std']).reset_index().sort_values('viewing')

print('All points:')
print(precision_summary)
print('')
print('Central points:')
print(precision_summary_cenrtal)

# t-tests to test difference between monocular and binocular viewing
# Separate data by viewing condition
binocular_data = mae_subject[mae_subject['viewing'] == 'binocular']
monocular_data = mae_subject[mae_subject['viewing'] == 'monocular']

# Variables to test
variables = ['ae x', 'ae y', 'R']

# Perform t-tests
for var in variables:
    # Extract data for each variable
    binoc_values = binocular_data[var]
    monoc_values = monocular_data[var]

    # Perform independent t-test
    t_stat, p_value = stats.ttest_ind(binoc_values, monoc_values)
    
    # Print results
    print(f'Test for {var}:')
    print(f'  T-statistic: {t_stat:.4f}')
    print(f'  P-value: {p_value:.4f}')
    print()

if check_normality_flag:
    check_normality(sd_subject[sd_subject['viewing'] == 'monocular']['precision x SD'])
    check_normality(sd_subject[sd_subject['viewing'] == 'monocular']['precision y SD'])
    check_normality(sd_subject[sd_subject['viewing'] == 'binocular']['precision x SD'])
    check_normality(sd_subject[sd_subject['viewing'] == 'binocular']['precision y SD'])

#%%
# precision S2S
melted_s2s_subject = s2s_subject.melt(id_vars=['subject ID', 'viewing', 'eye'], 
                                      value_vars=['precision x S2S', 'precision y S2S', 'precision R S2S'], 
                                      var_name='precision type', value_name='precision value')
melted_s2s_subject['precision type'] = melted_s2s_subject['precision type'].replace({
    'precision x S2S': 'x',
    'precision y S2S': 'y',
    'precision R S2S': 'R'})

melted_s2s_subject_central = s2s_subject_central.melt(id_vars=['subject ID', 'viewing', 'eye'], 
                                                      value_vars=['precision x S2S', 'precision y S2S', 'precision R S2S'], 
                                                      var_name='precision type', value_name='precision value')
melted_s2s_subject_central['precision type'] = melted_s2s_subject_central['precision type'].replace({
    'precision x S2S': 'x',
    'precision y S2S': 'y',
    'precision R S2S': 'R'})
# precision per monocular and binocular with both eye together
figure3, axs3 = plt.subplots(1,2, figsize=(12, 6))
sns.boxplot(x='precision type', y='precision value', hue='viewing', data=melted_s2s_subject,
            ax=axs3[0], showfliers=False)
sns.stripplot(x='precision type', y='precision value', hue='viewing', data=melted_s2s_subject, 
              dodge=True, alpha=0.7, ax=axs3[0], size=10, 
              edgecolor='white', linewidth=2, legend=False)


axs3[0].set_ylim([0, 0.35])
axs3[0].set_xlabel('')  
axs3[0].set_ylabel('')
axs3[0].legend_.remove()

sns.boxplot(x='precision type', y='precision value', hue='viewing', data=melted_s2s_subject_central,
            ax=axs3[1], showfliers=False)
sns.stripplot(x='precision type', y='precision value', hue='viewing', data=melted_s2s_subject_central, 
              dodge=True, alpha=0.7, ax=axs3[1], size=10, 
              edgecolor='white', linewidth=2, legend=False)
axs3[1].set_ylim([0, 0.35])
axs3[1].set_xlabel('')
axs3[1].set_ylabel('')

# Simplify legend by removing the word "viewing"
handles, labels = axs3[1].get_legend_handles_labels()
new_labels = [label.replace('viewing', '').strip() for label in labels]
axs3[1].legend(handles, new_labels, title='', loc='upper left', bbox_to_anchor=(1, 1))

figure3.align_ylabels()

# Set a shared y-label
figure3.text(0.04, 0.5, 's2s ($^\circ$)', va='center', rotation='vertical', fontsize=12)

plt.show()

figure3.savefig(f'{figures_dir}/S2S boxplot.png', bbox_inches='tight')

precision_summary = melted_s2s_subject.groupby(['viewing', 'precision type'])['precision value'].agg(['mean', 'std']).reset_index().sort_values('viewing')
precision_summary_cenrtal = melted_s2s_subject_central.groupby(['viewing', 'precision type'])['precision value'].agg(['mean', 'std']).reset_index().sort_values('viewing')

print('All points:')
print(precision_summary)
print('')
print('Central points:')
print(precision_summary_cenrtal)

# t-tests to test difference between monocular and binocular viewing
# Separate data by viewing condition
binocular_data = mae_subject[mae_subject['viewing'] == 'binocular']
monocular_data = mae_subject[mae_subject['viewing'] == 'monocular']

# Variables to test
variables = ['ae x', 'ae y', 'R']

# Perform t-tests
for var in variables:
    # Extract data for each variable
    binoc_values = binocular_data[var]
    monoc_values = monocular_data[var]

    # Perform independent t-test
    t_stat, p_value = stats.ttest_ind(binoc_values, monoc_values)
    
    # Print results
    print(f'Test for {var}:')
    print(f'  T-statistic: {t_stat:.4f}')
    print(f'  P-value: {p_value:.4f}')
    print()

if check_normality_flag:
    check_normality(s2s_subject[s2s_subject['viewing'] == 'monocular']['precision x S2S'])
    check_normality(s2s_subject[s2s_subject['viewing'] == 'monocular']['precision y S2S'])
    check_normality(s2s_subject[s2s_subject['viewing'] == 'binocular']['precision x S2S'])
    check_normality(s2s_subject[s2s_subject['viewing'] == 'binocular']['precision y S2S'])

#%% 
# calculate MAE for vergence and show in figure with error bars
vergence_data = data_no_outliers[data_no_outliers['viewing'] == 'binocular']
mae_vergence = vergence_data.groupby(['stimulus ID'])[['ae vergence', 
                                                       'stimulus position x', 
                                                       'stimulus position y']].mean()
vergence_data_central = data_no_outliers_central[data_no_outliers_central['viewing'] == 'binocular']
mae_vergence_central = vergence_data_central.groupby(['stimulus ID'])[['ae vergence', 
                                                       'stimulus position x', 
                                                       'stimulus position y']].mean()
               
figure1 = plt.figure(figsize=(10, 6))
sns.scatterplot(x='stimulus position x',
                y='stimulus position y',
                data=data_stimuli,
                color='black',
                s=50,
                figure=figure1)
# Add error bars using Matplotlib
plt.errorbar(x=mae_vergence['stimulus position x'], 
             y=mae_vergence['stimulus position y'], 
             yerr=mae_vergence['ae vergence'], 
             fmt='o', color='blue', 
             alpha=0.5, capsize=5, capthick=2, elinewidth=2)

plt.xlabel('Vertical stimulus position ($^\circ$)')
plt.ylabel('Horizontal stimulus position ($^\circ$)')
plt.show()

vergence_summary = mae_vergence['ae vergence'].agg(['mean', 'std']).reset_index()
vergence_summary_central = mae_vergence_central['ae vergence'].agg(['mean', 'std']).reset_index()