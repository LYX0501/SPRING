export MASTER_PORT=1061

data_dir=../../dataset

log_dir=${data_dir}/finetune/finetune_logs
save_dir=${data_dir}/finetune/finetune_checkpoints
mkdir -p $log_dir $save_dir

bpe_dir=../../utils/BPE
user_dir=../../ofa_module

data=${data_dir}/simmc2/simmc2_novisual_train.tsv,${data_dir}/simmc2/simmc2_novisual_dev.tsv
restore_file=./checkpoint.pt
selected_cols=0,1,2,3

task=simmc2
arch=ofa_base
criterion=adjust_label_smoothed_cross_entropy
label_smoothing=0.1
lr=4e-5
max_epoch=50
warmup_ratio=0.06
batch_size=24
update_freq=4
resnet_drop_path_rate=0.0
encoder_drop_path_rate=0.25
decoder_drop_path_rate=0.25
dropout=0.25
attention_dropout=0.25
max_src_length=512
max_tgt_length=40
num_bins=1000
patch_image_size=256
eval_cider_cached=${data_dir}/cider_cached_tokens/coco-valid-words.p
drop_worst_ratio=0.2
val_save_interval=5


for warmup_ratio in {0.06,}; do
  echo "warmup_ratio "${warmup_ratio}
  for drop_worst_after in {6000,}; do
    echo "drop_worst_after "${drop_worst_after}

    log_file=${log_dir}/$1".log"
    save_path=${save_dir}/$1
    mkdir -p $save_path

    CUDA_VISIBLE_DEVICES=$2 python3 -m torch.distributed.launch --nproc_per_node=$3 --master_port=${MASTER_PORT} ../../train.py \
        $data \
        --selected-cols=${selected_cols} \
        --bpe-dir=${bpe_dir} \
        --user-dir=${user_dir} \
        --restore-file=${restore_file} \
        --reset-optimizer --reset-dataloader --reset-meters \
        --save-dir=${save_path} \
        --task=${task} \
        --arch=${arch} \
        --criterion=${criterion} \
        --label-smoothing=${label_smoothing} \
        --batch-size=${batch_size} \
        --update-freq=${update_freq} \
        --encoder-normalize-before \
        --decoder-normalize-before \
        --share-decoder-input-output-embed \
        --share-all-embeddings \
        --layernorm-embedding \
        --patch-layernorm-embedding \
        --code-layernorm-embedding \
        --resnet-drop-path-rate=${resnet_drop_path_rate} \
        --encoder-drop-path-rate=${encoder_drop_path_rate} \
        --decoder-drop-path-rate=${decoder_drop_path_rate} \
        --dropout=${dropout} \
        --attention-dropout=${attention_dropout} \
        --weight-decay=0.01 --optimizer=adam --adam-betas="(0.9,0.999)" --adam-eps=1e-08 --clip-norm=1.0 \
        --lr-scheduler=polynomial_decay --lr=${lr} \
        --max-epoch=${max_epoch} --warmup-ratio=${warmup_ratio} \
        --log-format=simple --log-interval=10 \
        --fixed-validation-seed=7 \
        --no-epoch-checkpoints --keep-best-checkpoints=1 \
        --save-interval=${val_save_interval} --validate-interval=${val_save_interval} \
        --save-interval-updates=100 --validate-interval-updates=100 \
        --eval-cider \
        --eval-cider-cached-tokens=${eval_cider_cached} \
        --eval-args='{"beam":5,"max_len_b":40,"no_repeat_ngram_size":3}' \
        --best-checkpoint-metric=cider --maximize-best-checkpoint-metric \
        --max-src-length=${max_src_length} \
        --max-tgt-length=${max_tgt_length} \
        --find-unused-parameters \
        --freeze-encoder-embedding \
        --freeze-decoder-embedding \
        --add-type-embedding \
        --scale-attn \
        --scale-fc \
        --scale-heads \
        --disable-entangle \
        --num-bins=${num_bins} \
        --patch-image-size=${patch_image_size} \
        --drop-worst-ratio=${drop_worst_ratio} \
        --drop-worst-after=${drop_worst_after} \
        --fp16 \
        --fp16-scale-window=512 \
        --num-workers=0 
  done
done
