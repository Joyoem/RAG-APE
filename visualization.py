import matplotlib.pyplot as plt
import numpy as np

COLOR_BASE = "#DCE1E5"       
COLOR_EN_OUR = "#004B87"     
COLOR_ZH_OUR = "#008080"     
COLOR_ROUGE_BASE = "#F3D1F4" 
COLOR_ROUGE_OUR = "#7209B7"  

plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial']
plt.rcParams['axes.unicode_minus'] = False

metrics_data = {
    "en": {
        "base_bleu": 0.0524,  "our_bleu": 0.1124,
        "base_rouge": 0.2069, "our_rouge": 0.2540,
        "base_clarity": 2.9703, "our_clarity": 4.9531,
        "base_accuracy": 3.9596, "our_accuracy": 4.9531,
        "base_objectivity": 1.9992, "our_objectivity": 4.9906
    },
    "zh": {
        "base_bleu": 0.0372,  "our_bleu": 0.1630,
        "base_rouge": 0.0005, "our_rouge": 0.0048,
        "base_clarity": 2.9964, "our_clarity": 5.0000,
        "base_accuracy": 3.9904, "our_accuracy": 5.0000,
        "base_objectivity": 2.0060, "our_objectivity": 5.0000
    }
}

def draw_poster_nlp():
    languages = ['English Track\n(3,840 Samples)', 'Chinese Track\n(837 Samples)']
    base_bleu = [metrics_data['en']['base_bleu'], metrics_data['zh']['base_bleu']]
    our_bleu = [metrics_data['en']['our_bleu'], metrics_data['zh']['our_bleu']]
    base_rouge = [metrics_data['en']['base_rouge'], metrics_data['zh']['base_rouge']]
    our_rouge = [metrics_data['en']['our_rouge'], metrics_data['zh']['our_rouge']]

    x = np.arange(len(languages))
    width = 0.18

    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
    ax.setBackgroundColor = 'white'

    rects1 = ax.bar(x - width*1.5, base_bleu, width, label='Base Qwen (BLEU)', color=COLOR_BASE, edgecolor='#A2A2A2', linewidth=1)
    rects2 = ax.bar(x - width*0.5, our_bleu, width, label='Our System (BLEU-Relative Gain🚀)', color=COLOR_EN_OUR, edgecolor='#002B54', linewidth=1.2)
    rects3 = ax.bar(x + width*0.5, base_rouge, width, label='Base Qwen (ROUGE-L)', color=COLOR_ROUGE_BASE, edgecolor='#C499C5', linewidth=1)
    rects4 = ax.bar(x + width*1.5, our_rouge, width, label='Our System (ROUGE-L)', color=COLOR_ROUGE_OUR, edgecolor='#43036F', linewidth=1.2)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_color('#2C3E50')
    ax.spines['bottom'].set_linewidth(2)

    ax.grid(axis='y', linestyle='--', alpha=0.5, color='#BDC3C7')

    ax.set_ylabel('Score (0.0 - 1.0)', fontsize=14, fontweight='bold', color='#2C3E50')
    ax.set_title('Traditional Word Overlap Verification (BLEU & ROUGE)', fontsize=16, fontweight='bold', color='#004B87', pad=25)
    ax.set_xticks(x)
    ax.set_xticklabels(languages, fontsize=13, fontweight='bold', color='#2C3E50')
    ax.legend(frameon=True, facecolor='white', edgecolor='none', fontsize=11, loc='upper right')
    ax.set_ylim(0, 0.35)

    for rects in [rects1, rects2, rects3, rects4]:
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height:.4f}',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 4), textcoords="offset points",
                        ha='center', va='bottom', fontsize=10, fontweight='bold', color='#2C3E50')

    fig.tight_layout()
    plt.savefig('./poster_nlp_metrics.png', bbox_inches='tight', transparent=False, facecolor='white')
    plt.close()
    print(" saved as poster_nlp_metrics.png")

def draw_poster_judge():
    categories = ['Clarity\n(清晰度)', 'Accuracy\n(准确度)', 'Objectivity\n(客观性/洗净违禁词)']
    
    en_base = [metrics_data['en']['base_clarity'], metrics_data['en']['base_accuracy'], metrics_data['en']['base_objectivity']]
    en_our = [metrics_data['en']['our_clarity'], metrics_data['en']['our_accuracy'], metrics_data['en']['our_objectivity']]
    
    zh_base = [metrics_data['zh']['base_clarity'], metrics_data['zh']['base_accuracy'], metrics_data['zh']['base_objectivity']]
    zh_our = [metrics_data['zh']['our_clarity'], metrics_data['zh']['our_accuracy'], metrics_data['zh']['our_objectivity']]
    
    x = np.arange(len(categories))
    width = 0.35

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6), dpi=300)

    rects1 = ax1.bar(x - width/2, en_base, width, label='Base Qwen-1.5B', color=COLOR_BASE, edgecolor='#A2A2A2')
    rects2 = ax1.bar(x + width/2, en_our, width, label='Our RAG+SFT System', color=COLOR_EN_OUR, edgecolor='#002B54', linewidth=1.5)
    ax1.set_ylabel('Scores (1 - 5)', fontsize=13, fontweight='bold', color='#2C3E50')
    ax1.set_title('English Evaluation (3,840 Samples Cross-Review)', fontsize=14, fontweight='bold', color='#004B87', pad=15)
    ax1.set_xticks(x)
    ax1.set_xticklabels(categories, fontsize=11, fontweight='bold', color='#2C3E50')
    ax1.set_ylim(0, 5.8)
    ax1.grid(axis='y', linestyle='--', alpha=0.4)
    ax1.legend(loc='upper left', fontsize=11, frameon=True)

    rects3 = ax2.bar(x - width/2, zh_base, width, label='Base Qwen-1.5B', color=COLOR_BASE, edgecolor='#A2A2A2')
    rects4 = ax2.bar(x + width/2, zh_our, width, label='Our RAG+SFT System', color=COLOR_ZH_OUR, edgecolor='#004D4D', linewidth=1.5)
    ax2.set_title('Chinese Evaluation (837 Samples Cross-Review)', fontsize=14, fontweight='bold', color='#008080', pad=15)
    ax2.set_xticks(x)
    ax2.set_xticklabels(categories, fontsize=11, fontweight='bold', color='#2C3E50')
    ax2.set_ylim(0, 5.8)
    ax2.grid(axis='y', linestyle='--', alpha=0.4)
    ax2.legend(loc='upper left', fontsize=11, frameon=True)

    for ax in [ax1, ax2]:
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_color('#2C3E50')
        ax.spines['bottom'].set_linewidth(2)

    for ax, r_b, r_o in [(ax1, rects1, rects2), (ax2, rects3, rects4)]:
        for r in r_b + r_o:
            height = r.get_height()
            text_color = '#2E7D32' if height >= 4.9 else '#2C3E50'
            ax.annotate(f'{height:.2f}',
                        xy=(r.get_x() + r.get_width() / 2, height),
                        xytext=(0, 5), textcoords="offset points",
                        ha='center', va='bottom', fontsize=11, fontweight='bold', color=text_color)
            
    fig.suptitle('Human-Aligned AD Quality Breakthrough (VideoA11y Metrics Standard)', fontsize=18, fontweight='bold', y=1.02, color='#2C3E50')
    fig.tight_layout()
    plt.savefig('./poster_judge_comparison.png', bbox_inches='tight', transparent=False, facecolor='white')
    plt.close()
    print(" saved as poster_judge_comparison.png")

if __name__ == "__main__":
    draw_poster_nlp()
    draw_poster_judge()
    