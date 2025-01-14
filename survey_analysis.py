# Initial imports and environment setting.

%matplotlib inline
import numpy as np
import pandas as pd
from textwrap import wrap

import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 16})

import seaborn as sns
sns.set(context='talk', style='white')

import warnings
warnings.filterwarnings('ignore')

# Load in the data. This spreadsheet is (almost) direct from SurveyMonkey,
# though IP addresses, access dates, and free-text responses were scrubbed
# to anonymize respondents.

df = pd.read_csv('public_survey_data.csv', sep=',')

# SurveyMonkey provides an odd nesting of responses when exporting results.
# We'd like to convert this structure to a pandas MultiIndex data frame.
# First, let's find question indices -- adapted from https://stackoverflow.com/a/49584888

indices = [i for i, c in enumerate(df.columns) if not c.startswith('Unnamed')]
slices = [slice(i, j) for i, j in zip(indices, indices[1:] + [None])]
repeats = [len(range(*slice.indices(len(df.columns)))) for slice in slices]

# Now let's grab all of the questions and each of the options provided as possible responses.

questions = [c for c in df.columns if not c.startswith('Unnamed')]
options = df.iloc[:1].values[0].tolist()

# We can pair each possible response with its associated question...

matched_questions = []
for index, question in enumerate(questions):
    matched_questions += [question] * repeats[index]

# ...and create a new dataframe named 'responses' that correctly pairs questions and responses.

index = pd.MultiIndex.from_arrays([matched_questions, options],
                                  names=('question', 'options'))
data = df.iloc[2:].values
responses = pd.DataFrame(data=data, columns=index)

# First demographic questions -- the normalize keyword converts to percentages.
responses['Are you a member of OHBM?',
          'Response'].value_counts(normalize=True)

responses['What geographic region are you currently located in?',
          'Response'].value_counts(normalize=True)

responses['What is your current career status?',
          'Response'].value_counts(normalize=True)


def plot_stacked_bar(df, figwidth=12.5, textwrap=30):
    """
    A wrapper function to create a stacked bar plot.
    Seaborn does not implement this directly, so
    we'll use seaborn styling in matplotlib.

    Inputs
    ------

    figwidth: float
        The desired width of the figure. Also controls
        spacing between bars.

    textwrap: int
        The number of characters (including spaces) allowed
        on a line before wrapping to a newline.
    """
    reshape = pd.melt(df, var_name='option', value_name='rating')
    stack = reshape.rename_axis('count').reset_index().groupby(['option', 'rating']).count().reset_index()

    fig, ax = plt.subplots(1, 1, figsize=(15, figwidth))
    bottom = np.zeros(len(stack['option'].unique()))
    clrs = sns.color_palette('Set1', n_colors=4)  # to do: check colorblind friendly-ness
    # labels = ['Not aware', 'Aware but not engage',
    #           'Aware and occassionally engage', 'Aware and engaged']
    labels = ['Unsure', 'Not relevant', 'Somewhat relevant',
              'Relevant only to annual meeting', 'Consistently relevant']

    for i, rating in enumerate(np.unique(stack['rating'])):
        stackd = stack.query(f"rating == '{rating}'")
        ax.barh(y=stackd['option'], width=stackd['count'], left=bottom,
                tick_label=['\n'.join(wrap(s, textwrap)) for s in stackd['option']],
                color=clrs[i], label=labels[i])
        bottom += stackd['count'].to_numpy()

    sns.despine()
    ax.set_xlabel('Count', labelpad=20)
    ax.legend(title='Rating', bbox_to_anchor=(1, 1))

    return ax


# Next, we'd like to look at results
# 'How would you describe the content on the OHBM job board?',

content_questions = [
    'How would you describe the content in OHBM emails?',
    'How would you describe the content in the OHBM blog?',
    'How would you describe the content on OHBM Twitter?',
    'How would you describe the content in the NeuroSalience podcast?',
    'How would you describe the content in OHBM Facebook?',
    'How would you describe the content in OHBM YouTube?',
    'How would you describe the content in OHBM LinkedIn?',
    'How would you describe the content in OHBM OnDemand?',
    ]

content_responses = responses[content_questions]
ax = plot_stacked_bar(content_responses, figwidth=15, textwrap=35)
fig = ax.figure
fig.savefig('content.png', dpi=150, bbox_inches='tight')
