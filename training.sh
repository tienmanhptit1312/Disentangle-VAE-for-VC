#python train_acvae.py --dataset_fp=/home/ubuntu/vcc2018_WORLD_dataset --latent-size=32 --log_dir=VC_logs3/VCC2018_gvae_mcc_32_128_beta0.1_origin --epochs=200000000000000000 --report-interval=100 --lr=1e-4 --samples_length=128 --batch-size=8 --style_cof=10 --mse_cof=1

#python train_acvae.py --dataset_fp=/home/ubuntu/vcc2018_WORLD_dataset --latent-size=32 --log_dir=VC_logs3/VCC2018_gvae_mcc_32_128_beta0.1_spk_6 --epochs=200000000000000000 --report-interval=100 --lr=1e-4 --samples_length=128 --batch-size=8 --style_cof=10 --mse_cof=10 --style_cof=0.1 --speaker_size=6

python train.py --dataset_fp=/root/vcc2020_training_DisVAE --latent-size=32  --epochs=200000000000000000 --report-interval=500 --lr=1e-4 --samples_length=128 --batch-size=8 --style_cof=10 --mse_cof=10 --style_cof=0.1 --speaker_size=6 --train true
