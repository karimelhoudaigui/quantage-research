"""One forward-pass numerical diagnostic, not a semantic benchmark."""
import argparse
import json
import os
from pathlib import Path
import time


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--dtype', choices=('float16', 'bfloat16'), required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    os.environ.update(HF_HOME=str(Path.cwd() / 'research/external/models/hf-local'),
                      HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', HF_HUB_DISABLE_IMPLICIT_TOKEN='1',
                      HF_HUB_DISABLE_TELEMETRY='1', TOKENIZERS_PARALLELISM='false')
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    started = time.perf_counter()
    torch.set_num_threads(4)
    directory = Path('research/external/models/qwen2.5-1.5b-989aa79')
    tokenizer = AutoTokenizer.from_pretrained(directory, local_files_only=True, trust_remote_code=False)
    model = AutoModelForCausalLM.from_pretrained(directory, local_files_only=True, trust_remote_code=False,
              use_safetensors=True, torch_dtype=getattr(torch, a.dtype), attn_implementation='sdpa')
    model.eval()
    case = sorted(json.loads(Path('runs/20261113-c14-model-scale/cases.json').read_text()), key=lambda x:x['id'])[0]
    messages = [{'role':'system','content':Path('runs/20261113-c09-heldout-guard/instructions.md').read_text()},
                {'role':'user','content':json.dumps(case['request'], ensure_ascii=False)}]
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(text, return_tensors='pt')
    with torch.inference_mode():
        logits = model(**inputs).logits[0, -1, :].float()
    result = {'dtype':a.dtype, 'case_id':case['id'], 'vocabulary_logits':int(logits.numel()),
              'finite_logits':int(torch.isfinite(logits).sum()), 'nan_logits':int(torch.isnan(logits).sum()),
              'infinite_logits':int(torch.isinf(logits).sum()), 'argmax_token_id':int(logits.argmax()),
              'argmax_text':tokenizer.decode([int(logits.argmax())]), 'wall_seconds':time.perf_counter()-started,
              'generation_calls':0, 'scope':'prefill diagnostic on same input, not model semantic performance'}
    a.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
