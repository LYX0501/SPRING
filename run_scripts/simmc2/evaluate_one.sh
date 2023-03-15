export MASTER_PORT=1091

bpe_dir=/root/code/SPRING/utils/BPE
user_dir=/root/code/SPRING/ofa_module

para_result=/root/data/xican/finetune/finetune_checkpoints/$1
para=${para_result}/checkpoint_best.pt

data=/root/data/xican/simmc2/simmc2_novisual_devtest.tsv
selected_cols=0,1,2,3
split='test'

generation_pred_json=${para_result}/test_predict.json
split_path=/root/data/xican/simmcdata/simmc2_dials_dstc10_devtest.json
save_path=${para_result}/subtask-4-generation.json


CUDA_VISIBLE_DEVICES=$2 python3 -m torch.distributed.launch --nproc_per_node=$3 --master_port=${MASTER_PORT} /root/code/SPRING/evaluate.py \
    ${data} \
    --path=${para} \
    --user-dir=${user_dir} \
    --task=simmc2 \
    --batch-size=48 \
    --log-format=simple --log-interval=10 \
    --seed=7 \
    --gen-subset=${split} \
    --results-path=${para_result} \
    --beam=5 \
    --max-len-b=40 \
    --no-repeat-ngram-size=8 \
    --fp16 \
    --num-workers=0 \
    --model-overrides="{\"data\":\"${data}\",\"bpe_dir\":\"${bpe_dir}\",\"eval_cider\":False,\"selected_cols\":\"${selected_cols}\"}"


python3 /root/code/SPRING/run_scripts/simmc2/format_task4_generation.py \
    --generation-pred-json=${generation_pred_json} \
    --split-path=${split_path} \
    --save-path=${save_path}


python3 /root/code/SPRING/run_scripts/simmc2/response_evaluation_forall.py \
    --data_json_path=${split_path} \
    --model_response_path=${save_path} \
    --bleu_path=${para_result} \
    --para_name=${para} \
    --single_round_evaluation


