"""Treino LoRA com Hugging Face Trainer (sem TRL, para evitar quebra de versão)."""
import random

import torch


def treinar(exemplos, saida="modelo/lora_qwen15b", base="Qwen/Qwen2.5-1.5B-Instruct",
            epocas=2, lr=2e-4, r=16, alpha=32, max_len=1400, seed=42):
    from peft import LoraConfig, get_peft_model
    from transformers import AutoModelForCausalLM, AutoTokenizer, DataCollatorForSeq2Seq, Trainer, TrainingArguments

    random.seed(seed); torch.manual_seed(seed)
    tok = AutoTokenizer.from_pretrained(base)
    model = AutoModelForCausalLM.from_pretrained(base, torch_dtype=torch.float32, device_map="auto")
    model.config.use_cache = False
    model.gradient_checkpointing_enable()
    model.enable_input_require_grads()
    cfg = LoraConfig(r=r, lora_alpha=alpha, lora_dropout=0.05, task_type="CAUSAL_LM",
                     target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"])
    model = get_peft_model(model, cfg)
    model.print_trainable_parameters()

    dados, descartados = [], 0
    for ex in exemplos:
        prompt = tok.apply_chat_template(ex["messages"], tokenize=False, add_generation_prompt=True)
        p_ids = tok(prompt, add_special_tokens=False)["input_ids"]
        c_ids = tok(prompt + ex["alvo"] + "<|im_end|>\n", add_special_tokens=False)["input_ids"]
        if len(c_ids) > max_len:
            descartados += 1
            continue
        dados.append({"input_ids": c_ids, "attention_mask": [1] * len(c_ids),
                      "labels": [-100] * len(p_ids) + c_ids[len(p_ids):]})  # só aprende a resposta
    print(f"{len(dados)} exemplos de treino ({descartados} descartados por tamanho)")

    args = TrainingArguments(
        output_dir="modelo/_tmp", per_device_train_batch_size=2, gradient_accumulation_steps=8,
        num_train_epochs=epocas, learning_rate=lr, lr_scheduler_type="cosine", warmup_ratio=0.05,
        fp16=True, logging_steps=5, save_strategy="no", report_to="none", seed=seed, optim="adamw_torch")
    trainer = Trainer(model=model, args=args, train_dataset=dados,
                      data_collator=DataCollatorForSeq2Seq(tok, padding=True, label_pad_token_id=-100))
    trainer.train()
    model.save_pretrained(saida)
    tok.save_pretrained(saida)
    return trainer.state.log_history
