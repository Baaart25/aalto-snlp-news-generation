import glob
import json
import os

import click
import datasets
import pandas as pd


@click.command()
@click.argument('generated_file')  # path to the json file
@click.argument('results_file')
def main(generated_file, results_file):
    rouge = datasets.load_metric("rouge")
    # rouge = evaluate.load("rouge")

    df = pd.read_json(generated_file, lines=True)

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
