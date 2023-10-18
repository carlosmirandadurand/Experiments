import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

## FIRST DRAFT COMMIT - Pending testing....


#%%
# Setup input parameters and templates

model_name = "Writer/InstructPalmyra-20b"

instruction = "Describe a futuristic device that revolutionizes space travel."

PROMPT_DICT = {
    "prompt_input": (
        "Below is an instruction that describes a task, paired with an input that provides further context. "
        "Write a response that appropriately completes the request\n\n"
        "### Instruction:\n{instruction}\n\n### Input:\n{input}\n\n### Response:"
    ),
    "prompt_no_input": (
        "Below is an instruction that describes a task. "
        "Write a response that appropriately completes the request.\n\n"
        "### Instruction:\n{instruction}\n\n### Response:"
    ),
}

#%%
# Generate prompt text based on the templates and input parameters

text = (
    PROMPT_DICT["prompt_no_input"].format(instruction=instruction)
        if not input
            else PROMPT_DICT["prompt_input"].format(instruction=instruction, input=input)
)

print("text:\n", text, "\n\n")


#%%
# Setup input parameters

tokenizer = AutoTokenizer.from_pretrained(model_name)

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="auto",
    torch_dtype=torch.float16
)

model_inputs = tokenizer(text, return_tensors="pt").to("cuda")
output_ids = model.generate(
    **model_inputs,
    max_length=256,
)
output_text = tokenizer.batch_decode(output_ids, skip_special_tokens=True)[0]
clean_output = output_text.split("### Response:")[1].strip()

print(clean_output)




# (azure_datascience_20231002_win) C:\Users\CarlosMirandaDurand\OneDrive - Proactive Ingredient LLC\Documents\Code\Experiments>C:/Users/CarlosMirandaDurand/miniconda3/envs/azure_datascience_20231002_win/python.exe "c:/Users/CarlosMirandaDurand/OneDrive - Proactive Ingredient LLC/Documents/Code/Experiments/other/palmira.py"
# Special tokens have been added in the vocabulary, make sure the associated word embeddings are fine-tuned or trained.
# Downloading (…)model.bin.index.json: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 39.9k/39.9k [00:00<00:00, 20.0MB/s]
# C:\Users\CarlosMirandaDurand\miniconda3\envs\azure_datascience_20231002_win\Lib\site-packages\huggingface_hub\file_download.py:133: UserWarning: `huggingface_hub` cache-system uses symlinks by default to efficiently store duplicated files but your machine does not support them in C:\Users\CarlosMirandaDurand\.cache\huggingface\hub. Caching files will still work but in a degraded version that might require more space on your disk. This warning can be disabled by setting the `HF_HUB_DISABLE_SYMLINKS_WARNING` environment variable. For more details, see https://huggingface.co/docs/huggingface_hub/how-to-cache#limitations.
# To support symlinks on Windows, you either need to activate Developer Mode or to run Python as an administrator. In order to see activate developer mode, see this article: https://docs.microsoft.com/en-us/windows/apps/get-started/enable-your-device-for-development
#   warnings.warn(message)
# Downloading (…)l-00001-of-00005.bin: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 9.93G/9.93G [03:55<00:00, 42.2MB/s]
# Downloading (…)l-00002-of-00005.bin: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 9.97G/9.97G [03:48<00:00, 43.5MB/s]
# Downloading (…)l-00003-of-00005.bin: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 9.97G/9.97G [03:48<00:00, 43.6MB/s]
# Downloading (…)l-00004-of-00005.bin: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 9.97G/9.97G [03:47<00:00, 43.8MB/s]
# Downloading (…)l-00005-of-00005.bin: 100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 680M/680M [00:15<00:00, 42.6MB/s]
# Downloading shards: 100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 5/5 [15:49<00:00, 189.97s/it]
# Traceback (most recent call last):
#   File "c:\Users\CarlosMirandaDurand\OneDrive - Proactive Ingredient LLC\Documents\Code\Experiments\other\palmira.py", line 7, in <module>
#     model = AutoModelForCausalLM.from_pretrained(
#             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "C:\Users\CarlosMirandaDurand\miniconda3\envs\azure_datascience_20231002_win\Lib\site-packages\transformers\models\auto\auto_factory.py", line 565, in from_pretrained
#     return model_class.from_pretrained(
#            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "C:\Users\CarlosMirandaDurand\miniconda3\envs\azure_datascience_20231002_win\Lib\site-packages\transformers\modeling_utils.py", line 3307, in from_pretrained
#     ) = cls._load_pretrained_model(
#         ^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "C:\Users\CarlosMirandaDurand\miniconda3\envs\azure_datascience_20231002_win\Lib\site-packages\transformers\modeling_utils.py", line 3428, in _load_pretrained_model
#     raise ValueError(
# ValueError: The current `device_map` had weights offloaded to the disk. Please provide an `offload_folder` for them. Alternatively, make sure you have `safetensors` installed if the model you are using offers the weights in this format.
