import torch
from torch.utils.data import DataLoader, Dataset, TensorDataset
import numpy as np 
import librosa
import os
import preprocessing.utils as processing
#import utils as processing
from functools import wraps
from time import time
import glob
import pickle

def timing(f):
    @wraps(f)
    def wrap(*args, **kw):
        ts = time()
        result = f(*args, **kw)
        te = time()
        print('func:%r args:[%r, %r] took: %2.4f sec' % \
          (f.__name__, args, kw, te-ts))
        return result
    return wrap

def get_col_txt(fp, col_number):

    token = open(fp, 'r')
    linestoken = token.readlines()
    result = []

    for line in linestoken:
        result.append(line.split()[col_number]) 

    del result[0]
    return result

def get_male_spk(fp):
    rmv_idx = []
    fp_spk_info = os.path.join(fp, 'speaker-info.txt')
    file_header = ['ID', 'AGE', 'GENDER', 'ACCENTS', 'REGION']

    spk_gender = get_col_txt(fp_spk_info, file_header.index('GENDER'))
    spk_id = get_col_txt(fp_spk_info, file_header.index('ID'))
    assert len(spk_gender) == len(spk_id)
    for idx in range(len(spk_gender)):
        if spk_gender[idx] == 'F':
            rmv_idx.append(idx)
            
    spk_id = [spk for idx, spk in enumerate(spk_id) if idx not in rmv_idx]
    return spk_id


class SpeechDataset(Dataset):
    def __init__(self, file_path,sr=16000, samples_length=32768, num_utterances=10):
        self.file_path =file_path
        self.sr = sr
        self.samples_length = samples_length
        self.num_utterances = num_utterances

        self.speaker_ids = [f for f in os.listdir(self.file_path)]
        self.utterance_ids = {}
        for speaker in self.speaker_ids:
            self.utterance_ids[speaker] = [f for f in os.listdir(os.path.join(self.file_path, speaker)) \
                                          if os.path.isfile(os.path.join(self.file_path, speaker, f))]

    def __getitem__(self, index):
        speaker_id = self.speaker_ids[index]
        utterances = []
        data = []
        speaker_ids = []
        for i in range(self.num_utterances):
            folder_path = os.path.join(self.file_path, speaker_id)
            rd_uttrance = np.random.choice(len(self.utterance_ids[speaker_id]), 1)[0]
            utterance = self.utterance_ids[speaker_id][rd_uttrance]
            fn = os.path.join(folder_path, utterance)
            wav, sr = librosa.load(fn, sr=self.sr)
            if len(wav) < self.samples_length:
                while len(wav) < self.samples_length:
                    # print('pick another wav')
                    rd_uttrance = np.random.choice(len(self.utterance_ids[speaker_id]), 1)[0]
                    utterance = self.utterance_ids[speaker_id][rd_uttrance]
                    fn = os.path.join(folder_path, utterance)
                    wav, sr = librosa.load(fn, sr=self.sr)
            rd_begin = np.random.choice((len(wav)-self.samples_length), 1)[0]
            wav = wav[rd_begin:rd_begin + self.samples_length]

            mel_spec = processing.melspectrogram(wav)
            # mel_spec = librosa.feature.melspectrogram(wav, sr=16000,n_fft=1024,
                                                    #   hop_length=256, )

            data.append(mel_spec)
            utterances.append(utterance)
            # speaker_ids.extend(speaker_id)
        data = torch.tensor(data)

        return data, utterances, speaker_id
    def __len__(self):
        return len(self.speaker_ids)

class SpeechDataset2(Dataset):
    def __init__(self, file_path,sr=16000, samples_length=67, num_utterances=10):
        self.file_path =file_path
        self.sr = sr
        self.samples_length = samples_length
        self.num_utterances = num_utterances

        self.speaker_ids = [f for f in os.listdir(self.file_path)]
        self.utterance_ids = {}
        for speaker in self.speaker_ids:
            self.utterance_ids[speaker] = [f for f in os.listdir(os.path.join(self.file_path, speaker)) \
                                          if os.path.isfile(os.path.join(self.file_path, speaker, f))]

    def __getitem__(self, index):
        speaker_id = self.speaker_ids[index]
        utterances = []
        data = []
        speaker_ids = []
        for i in range(self.num_utterances):
            folder_path = os.path.join(self.file_path, speaker_id)
            rd_uttrance = np.random.choice(len(self.utterance_ids[speaker_id]), 1)[0]
            utterance = self.utterance_ids[speaker_id][rd_uttrance]
            fn = os.path.join(folder_path, utterance)
            file = open(fn,'rb')
            mel_spec = pickle.load(file)
            if mel_spec.shape[1] < self.samples_length:
                while mel_spec.shape[1] < self.samples_length:
                    # print('size of utterance:{}, size:{}'.format(utterance, mel_spec.shape[1]))
                    # print('pick another wav')
                    rd_uttrance = np.random.choice(len(self.utterance_ids[speaker_id]), 1)[0]
                    utterance = self.utterance_ids[speaker_id][rd_uttrance]
                    fn = os.path.join(folder_path, utterance)
                    file = open(fn,'rb')
                    mel_spec = pickle.load(file)
            rd_begin = np.random.choice((mel_spec.shape[1] - self.samples_length), 1)[0]
            mel_spec = mel_spec[:,rd_begin:rd_begin + self.samples_length]

            # mel_spec = processing.melspectrogram(wav)
            # mel_spec = librosa.feature.melspectrogram(wav, sr=16000,n_fft=1024,
                                                    #   hop_length=256, )

            data.append(mel_spec)
            utterances.append(utterance)
            # speaker_ids.extend(speaker_id)
        data = torch.tensor(data)

        return data, utterances, speaker_id
    def __len__(self):
        return len(self.speaker_ids)

########## Dataset for loading mel from numpy file #####################################
class SpeechDataset3(Dataset):
    def __init__(self, file_path,sr=16000, samples_length=64, num_utterances=10, male_dataset=False):
        self.file_path =file_path
        self.sr = sr
        self.samples_length = samples_length
        self.num_utterances = num_utterances
        self.speaker_info_fp = os.path.join(self.file_path, 'speaker-info.txt')
        self.utterance_ids = {}


        if male_dataset:
            self.speaker_ids = get_male_spk(self.file_path)
        else:
            self.speaker_ids = [f for f in os.listdir(self.file_path)]
        
        for speaker in self.speaker_ids:
            self.utterance_ids[speaker] = glob.glob(os.path.join(self.file_path, speaker, '*.npy'))

    def __getitem__(self, index):
        speaker_id = self.speaker_ids[index]
        utterances = []
        data = []
        speaker_ids = []
        for i in range(self.num_utterances):
            folder_path = os.path.join(self.file_path, speaker_id)
            rd_uttrance = np.random.choice(len(self.utterance_ids[speaker_id]), 1)[0]
            utterance = self.utterance_ids[speaker_id][rd_uttrance]
            mel_spec = np.load(utterance)
            # transpose for new new_encoder2 dataset
            mel_spec = np.transpose(mel_spec, (1, 0))
            #print('mel spectrogram shape: ', mel_spec.shape)
            if mel_spec.shape[1] <= self.samples_length:
                while mel_spec.shape[1] < self.samples_length:
                    # print('size of utterance:{}, size:{}'.format(utterance, mel_spec.shape[1]))
                    # print('pick another wav')
                    rd_uttrance = np.random.choice(len(self.utterance_ids[speaker_id]), 1)[0]
                    utterance = self.utterance_ids[speaker_id][rd_uttrance]
                    # fn = os.path.join(folder_path, utterance)
                    # file = open(fn,'rb')
                    mel_spec = np.load(utterance)
            print('mel shape:  ',mel_spec.shape[1])
            i#print(': ', (mel_spec.shape[1] - self.samples_length))
            rd_begin = np.random.choice((mel_spec.shape[1] - self.samples_length), 1)[0]
            print('rd begin: ', rd_begin)
            # print()
            mel_spec = mel_spec[:,rd_begin:rd_begin + self.samples_length]
            #print('mel spectrogram shape: ', mel_spec.shape)
            data.append(mel_spec)
            utterances.append(utterance)
            speaker_ids.append(speaker_id)

        # print('data shape: ', data.shape)
        data = torch.tensor(data)
         
        return data, utterances, speaker_ids
    def __len__(self):
        return len(self.speaker_ids)
########################################################################################


@timing
def load_batch(loader):
    return next(iter(loader))


def speaker_to_onehot(speaker_ids, speaker_all,num_classes=109, num_utterance=40):
    # onehot_embedding = torch.nn.functional.one_hot(torch.arange(0,109), num_classes=109)
    # speaker_onehot = [speaker for speaker in speaker_ids for i in range(num_utterance)]
    # speaker_ids = [spea for spea in speaker_ids]
    speaker_onehot = np.empty((len(speaker_ids)*num_utterance), dtype=np.int16)
    for j in range(len(speaker_ids)):
        for i in range(num_utterance):
            idx = speaker_all.index(speaker_ids[j])
            # print(idx)
            speaker_onehot[j*num_utterance+i] = idx

    return torch.tensor(speaker_onehot) 


def dump_wav2spectrogram():
    import pickle
    file_path = '/home/ubuntu/VCTK-Corpus/new_encoder3/'
    mel_file_path = os.path.join('/home/manhlt/extra_disk/VCTK-Corpus/mel_spectrogram')
    if not os.path.exists(mel_file_path):
        os.mkdir(mel_file_path)

    speaker_ids = [speaker for speaker in os.listdir(file_path)]
    for speaker in speaker_ids:
        os.mkdir(os.path.join(mel_file_path, speaker))

    for speaker in speaker_ids:
        speaker_fp = os.path.join(file_path, speaker)
        speaker_mel_sp = os.path.join(mel_file_path, speaker)
        utterances = [f for f in os.listdir(speaker_fp) if os.path.isfile(os.path.join(speaker_fp, f))]
        for utterance in utterances:
            wav, sr = librosa.load(os.path.join(speaker_fp, utterance), sr=16000)
            mel_spec = processing.melspectrogram(wav)
            file = open(os.path.join(speaker_mel_sp, utterance+'.pkl'),'wb')
            pickle.dump(mel_spec, file)
            print('Processing: ',utterance)
    # print(speaker_ids)

if __name__=='__main__':
    # from vocoder2waveform import build_model
    # from vocoder2waveform import wavegen
    import librosa
    import numpy as np
    import librosa.display
    import matplotlib.pyplot as plt

    device = torch.device('cuda')
    file_path = '/home/ubuntu/VCTK-Corpus/new_encoder3'
    # ckpt_path = '/home/manhlt/extra_disk/checkpoint_step001000000_ema.pth'

    # plt.figure()
    # data = np.zeros((80,67), dtype=np.float)
    # data[0:10] = 0.5
    # data[11:20] = 0.01
    
    dataset = SpeechDataset3(file_path, samples_length=63)
    dataloader = DataLoader(dataset, num_workers=0, batch_size=2,
                            pin_memory=True, shuffle=True, drop_last=True)
    
    #### shape of utterances [utterances_id, speaker_ids] ############
    batch = load_batch(dataloader)
    # print(data[0][9])
    # print(len(utterances))
    # print(len(speaker_ids))
    print(batch[1][0][0])
    print('-----------------------------------------------------------------------------------')
    # print(utterances)
    # print(utterances)
    # print(speaker_ids)
    # mel_spec = data[0][0].cpu().numpy()
    # librosa.display.specshow(mel_spec, x_axis='time', y_axis='mel', sr=16000)
    # plt.colorbar(format='%f')
    # plt.title('My life is fuck up')

    # plt.show()
    # mel_spec2 = mel_spec
    # mel_spec2[:,:20] = 2
    # plt.figure()
    # librosa.display.specshow(mel_spec2, x_axis='time', y_axis='mel', sr=16000, fmax=8000)
    # plt.show()
    # onehot = speaker_to_onehot(speaker_ids, dataset.speaker_ids)

    # dump_wav2spectrogram()

    
    #     librosa.output.write_wav(utterance[i][0]+'.wav', wav, sr=16000)
