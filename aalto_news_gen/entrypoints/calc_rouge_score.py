import glob
import json
import os

import click
import datasets
import pandas as pd


@click.command()
@click.argument('references')  # path to original json file(s)
@click.argument('predicted')  # path to predicted json file
@click.argument('results_file')
def main(references, predicted, results_file):
    rouge = datasets.load_metric("rouge")
    # rouge = evaluate.load("rouge")

    files = [references] if os.path.isfile(references) else sorted(glob.glob(f'{references}/*.jsonl.gz'))
    site_dfs = []
    for file in files:
        site_df = pd.read_json(file, lines=True)
        site_df = site_df[['article', 'uuid']]
        site_df = site_df.astype('str')
        site_dfs.append(site_df)
    ref_df = pd.concat(site_dfs)
    pred_df = pd.read_json(predicted, lines=True)

    df = pd.merge(ref_df, pred_df, on='uuid')

    ref = df['article'].tolist()
    gen = df['generated'].tolist()

    rouge_output = rouge.compute(
        predictions=gen, references=ref, rouge_types=["rouge1", "rouge2", "rougeL"]
    )
    
    rouge1 = rouge_output["rouge1"].mid
    rouge2 = rouge_output["rouge2"].mid
    rougeL = rouge_output["rougeL"].mid

    rouge_scores = {
        "rouge1_precision": round(rouge1.precision, 4),
        "rouge1_recall": round(rouge1.recall, 4),
        "rouge1_fmeasure": round(rouge1.fmeasure, 4),
        "rouge2_precision": round(rouge2.precision, 4),
        "rouge2_recall": round(rouge2.recall, 4),
        "rouge2_fmeasure": round(rouge2.fmeasure, 4),
        "rougeL_precision": round(rougeL.precision, 4),
        "rougeL_recall": round(rougeL.recall, 4),
        "rougeL_fmeasure": round(rougeL.fmeasure, 4),
    }
    with open(results_file, 'w') as fp:
        json.dump(rouge_scores, fp)


if __name__ == '__main__':
    main()
