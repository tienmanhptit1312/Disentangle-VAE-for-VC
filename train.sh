#python jointly_train_emb_autoencoder.py --data_path=/home/ubuntu/VCTK-Corpus/new_encoder2 --emb_model_path=/home/ubuntu/train_normalize_data.pt --save_iter=10000  --lr=1e-3

python jointly_train_emb_autoencoder.py --utterances_per_batch=20  --data_path=/home/ubuntu/VIVOS_full_mel --emb_model_path=/home/ubuntu/vietnamese_spk_emb4.pt --save_path=/home/ubuntu/autovc_vietnamese_32/ --save_iter=10000  --lr=1e-3 

#python jointly_train_emb_autoencoder.py --utterances_per_batch=50 --data_path=/home/ubuntu/VCTK-Corpus/new_encoder2 --emb_model_path=/home/ubuntu/train_normalize_data.pt --save_path=/home/ubuntu/autovc_original_param/ --save_iter=10000  --lr=1e-3
