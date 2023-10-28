import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

new_price = {
    'accord': {
        'LX': 27895,
        'EX': 29110,
        'Hybrid': 32195,
        'EX-L': 33840,
        'Touring': 38190
    },
    'cr-v': {

    },
    'rav4': {
        'LE': 28475,
        'XLE': 29985,
        'XLE Premium': 32875,
        'Adventure': 34670,
        'TRD Off-Road': 38095,
        'Limited': 36780,
        'LE Hybrid': 31475,
        'XLE Hybrid': 32985,
        'SE Hybrid': 34170,
        'XSE Hybrid': 37135,
    },
    'camry': {
        'LE': 26420,
        'SE': 27960,
        'XLE': 31170,
        'XSE': 31720,
        'LE Hybrid': 28885,
        'SE Hybrid': 30390,
        'XLE Hybrid': 33745
    }
}

def extract_trim(row):
    if "accord" in row['model']:
        base = row['title'].split('Honda Accord')[1].strip()
    elif "cr-v" in row['model']:
        base = row['title'].split('Honda CR-V')[1].strip()
    elif "rav4" in row['model']:
        base = row['title'].split('Toyota RAV4')[1].strip()
    elif "camry" in row['model']:
        base = row['title'].split('Toyota Camry')[1].strip()
    else:
        base = None

    if base is None:
        return None

    if "Hybrid" not in base and row['hybrid']:
        base += ' Hybrid'

    return base


new_price_data = []

for model, trims in new_price.items():
    for trim, price in trims.items():
        new_price_data.append({
            'model': model,
            'trim': trim,
            'mileage': 0,  # because it's a new car
            'price': price
        })

new_price_df = pd.DataFrame(new_price_data)



df = pd.read_json("all_car_listings.json")

print(df.columns)

palette_dict = {'accord': sns.color_palette('deep')[0], 'cr-v': sns.color_palette('deep')[1],
                'camry': sns.color_palette('deep')[2], 'rav4': sns.color_palette('deep')[3],
                }

df['trim'] = df.apply(extract_trim, axis=1)
df = df[df['model'].isin(['accord', 'cr-v', 'camry', 'rav4'])]
df = pd.concat([df, new_price_df], ignore_index=True)

# filter out miles > 100k
df = df[df['miles'] < 100000]

models = ['accord', 'cr-v', 'rav4', 'camry']

sns.set(rc={"figure.figsize":(15, 15)})
sns.set_style("whitegrid")

df_combined = df

sns.set(rc={"figure.figsize":(10, 10)})
sns.set_style("whitegrid")

models = df_combined['model'].unique()

# Adjust this to 2 rows and 2 columns for the subplots
fig, axes = plt.subplots(2, 2)

for idx, model in enumerate(models):
    row = idx // 2
    col = idx % 2
    subset = df_combined[df_combined['model'] == model].sort_values(by='miles')
    sns.lineplot(data=subset, x='miles', y='price', hue='trim', ax=axes[row, col], palette='deep')
    axes[row, col].set_title(f'Price vs. Mileage for {model.capitalize()}')
    axes[row, col].set_ylabel('Price')
    axes[row, col].set_xlabel('Miles')
    # Optional: To limit the number of legend entries and prevent overlap
    handles, labels = axes[row, col].get_legend_handles_labels()
    axes[row, col].legend(handles=handles[1:], labels=labels[1:])

plt.tight_layout()
plt.show()
