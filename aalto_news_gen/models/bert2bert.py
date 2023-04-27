import glob
import os

import pandas as pd
import yaml
from datasets import Dataset, load_metric, DatasetDict
from transformers import EncoderDecoderModel, BertTokenizer, pipeline
from transformers import IntervalStrategy, Seq2SeqTrainingArguments, Seq2SeqTrainer

from aalto_news_gen.utils.config_reader import get_config_from_yaml


class Bert2Bert():
    def __init__(self, config_path):
        with open(config_path, 'r') as config_file:
            self.config = yaml.load(config_file, Loader=yaml.FullLoader)

        if self.config['load_model']:
            self.model = EncoderDecoderModel.from_pretrained(self.config['model_path'])
        else:
            self.model = EncoderDecoderModel.from_encoder_decoder_pretrained(
                self.config['tokenizer'], self.config['tokenizer']
            )

        self.tokenizer = BertTokenizer.from_pretrained(self.config['tokenizer'])

        self.model.config.decoder_start_token_id = self.tokenizer.cls_token_id
        self.model.config.pad_token_id = self.tokenizer.pad_token_id
        self.model.config.eos_token_id = self.tokenizer.sep_token_id
        self.model.config.vocab_size = self.model.config.encoder.vocab_size

    def load_dataset(self, data_dir, shuffle=True):
        files = [data_dir] if os.path.isfile(data_dir) else sorted(glob.glob(f'{data_dir}/*.jsonl.gz'))
        site_dfs = []
        for file in files:
            site_df = pd.read_json(file, lines=True)
            site_df = site_df[['article', 'uuid']]
            site_df = site_df.dropna()
            site_df = site_df.astype('str')
            site_dfs.append(site_df)
        df = pd.concat(site_dfs)
        if shuffle:
            df = df.sample(frac=1, random_state=123)
        return Dataset.from_pandas(df)

    def process_data_to_model_inputs(self, batch):
        # Tokenize the input and target data
        inputs = self.tokenizer(batch['article'], padding='max_length', truncation=True, max_length=512)
        outputs = self.tokenizer(batch['article'], padding='max_length', truncation=True, max_length=512)

        batch['input_ids'] = inputs.input_ids
        batch['attention_mask'] = inputs.attention_mask
        # batch["decoder_input_ids"] = outputs.input_ids
        batch['decoder_attention_mask'] = outputs.attention_mask
        batch['labels'] = outputs.input_ids.copy()

        batch['labels'] = [[-100 if token == self.tokenizer.pad_token_id else token for token in labels]
                           for labels in batch['labels']]

        return batch

    def tokenize_datasets(self, raw_datasets):
        return raw_datasets.map(self.process_data_to_model_inputs, batched=True, remove_columns=['article'])

    def _get_seq2seq_training_args(self):
        return Seq2SeqTrainingArguments(
            output_dir=self.config['output_dir'],
            learning_rate=self.config['learning_rate'],
            num_train_epochs=self.config['num_train_epochs'],
            per_device_train_batch_size=self.config['batch_size'],
            per_device_eval_batch_size=self.config['batch_size'],
            evaluation_strategy=IntervalStrategy.STEPS,
            weight_decay=self.config['weight_decay'],
            save_total_limit=self.config['save_total_limit'],
            eval_steps=self.config['valid_steps'],
            save_steps=self.config['valid_steps'],
            predict_with_generate=True,
            generation_max_length=self.config['max_predict_length'],
            generation_num_beams=self.config['num_beams'],
            warmup_steps=self.config['warmup_steps'],
            load_best_model_at_end=True,
            fp16=self.config['fp16'],
        )

    def _load_tokenized_dataset(self):
        if self.config['do_preprocess']:
            raw_datasets = DatasetDict()
            raw_datasets['train'] = self.load_dataset(self.config['train_dir'])
            raw_datasets['validation'] = self.load_dataset(self.config['valid_dir'])
            raw_datasets['test'] = self.load_dataset(self.config['test_dir'], shuffle=False)
            tokenized_datasets = self.tokenize_datasets(raw_datasets)
            if self.config['save_tokenized_data']:
                tokenized_datasets.save_to_disk(self.config['preprocessed_dataset_path'])
        else:
            tokenized_datasets = DatasetDict.load_from_disk(self.config['preprocessed_dataset_path'])
        return tokenized_datasets


    def get_seq2seq_trainer(self, tokenized_datasets, load_train_data=True) -> Seq2SeqTrainer:
        return Seq2SeqTrainer(
            model=self.model,
            args=self._get_seq2seq_training_args(),
            train_dataset=tokenized_datasets["train"] if load_train_data else None,
            eval_dataset=tokenized_datasets["validation"] if load_train_data else None,
        )

    def train(self):
        tokenized_datasets = self._load_tokenized_dataset()

        trainer = self.get_seq2seq_trainer(tokenized_datasets, load_train_data=True)

        # Training
        checkpoint = self.config['resume_from_checkpoint'] if self.config['resume_from_checkpoint'] else None
        train_output = trainer.train(resume_from_checkpoint=checkpoint)
        trainer.save_model(os.path.join(self.config['output_dir'], 'best_model'))

        # Evaluation
        metrics = trainer.evaluate(
            metric_key_prefix="eval",
            max_length=self.config['max_predict_length'],
            num_beams=self.config['num_beams'],
            length_penalty=self.config['length_penalty'],
            no_repeat_ngram_size=self.config['no_repeat_ngram_size'],
            encoder_no_repeat_ngram_size=self.config['encoder_no_repeat_ngram_size'],
            early_stopping=self.config['generate_early_stopping'],
        )
        trainer.save_metrics("eval", metrics)

    def predict_pipeline(self, text):
        nlp = pipeline(task='text-generation', model=self.model, tokenizer=self.tokenizer)
        return nlp(text,
                   max_length=self.config['max_predict_length'],
                   num_beams=self.config['num_beams'],
                   length_penalty=self.config['length_penalty'],
                   no_repeat_ngram_size=self.config['no_repeat_ngram_size'],
                   encoder_no_repeat_ngram_size=self.config['encoder_no_repeat_ngram_size'],
                   early_stopping=self.config['generate_early_stopping'],
                   )