"""Geração local com Hugging Face (modelo base + adaptador LoRA opcional)."""
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

MODELO_BASE = "Qwen/Qwen2.5-1.5B-Instruct"


class HFGen:
    def __init__(self, base=MODELO_BASE, adapter=None, dtype=torch.float16):
        self.tok = AutoTokenizer.from_pretrained(base)
        self.model = AutoModelForCausalLM.from_pretrained(base, torch_dtype=dtype, device_map="auto")
        self.tem_adapter = False
        if adapter:
            from peft import PeftModel
            self.model = PeftModel.from_pretrained(self.model, adapter)
            self.tem_adapter = True
        self.model.eval()

    @torch.no_grad()
    def gerar(self, mensagens, usar_adapter=False, max_new_tokens=256):
        prompt = self.tok.apply_chat_template(mensagens, tokenize=False, add_generation_prompt=True)
        ids = self.tok(prompt, return_tensors="pt").to(self.model.device)
        kw = dict(max_new_tokens=max_new_tokens, do_sample=False, pad_token_id=self.tok.eos_token_id)
        if self.tem_adapter and not usar_adapter:
            with self.model.disable_adapter():
                out = self.model.generate(**ids, **kw)
        else:
            out = self.model.generate(**ids, **kw)
        return self.tok.decode(out[0][ids["input_ids"].shape[1]:], skip_special_tokens=True)
