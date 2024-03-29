from collections import defaultdict, deque
import datetime
import time
import torch
import torch.utils.data.dataset
import torch.distributed as dist

from sklearn.preprocessing import MultiLabelBinarizer, LabelEncoder
from PIL import Image, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
import pandas as pd
import numpy as np

import errno
import os

class LNMLocationDataset(torch.utils.data.dataset.Dataset):
    """Loading data from input file formatted as csv.
    """
    def __init__(self, infile=None, transform=None, df=None):
        self.transform = transform
        self.lbe = LabelEncoder()
        
        # Read csv file
        if df is None:
            df = pd.read_csv(infile)
            
        self.images = df['image_name']
        self.labels = self.lbe.fit_transform(df['tags'])
    
        self.classes = sorted(np.unique(df['tags']))
        self.class_to_idx = dict(zip(self.classes, range(0, len(self.classes))))
        
        self.imgs = list(zip(self.images, self.labels))
        self.root = '/media/storage1/project/deep_learning/ultrasound_tjmuch/ultrasound_tjmuch_data_20180105'

    def __getitem__(self, i):
        path = os.path.join(self.root, self.images[i])
        
        with open(path, 'rb') as f:
            img = Image.open(f)
            img = img.convert('RGB')
            
        if self.transform is not None:
            img = self.transform(img)

        label = torch.tensor(self.labels[i], dtype = torch.long)
        
        return img, label

    def __len__(self):
        return len(self.images)


class CSVDataset(torch.utils.data.dataset.Dataset):
    """Loading data from input file formatted as csv.
    """
    def __init__(self, infile=None, transform=None, df=None):
        self.transform = transform
        self.lbe = LabelEncoder()
        
        # Read csv file
        if df is None:
            df = pd.read_csv(infile)
            
        self.images = df['image_name']
        #self.labels = self.lbe.fit_transform(df['label'])
        self.labels = df['label']
    
        self.classes = sorted(np.unique(df['label']))
        self.class_to_idx = dict(zip(self.classes, range(0, len(self.classes))))
        
        self.imgs = list(zip(self.images, self.labels))

    def __getitem__(self, i):
        path = self.images[i]
        
        with open(path, 'rb') as f:
            img = Image.open(f)
            img = img.convert('RGB')
            
        if self.transform is not None:
            img = self.transform(img)

        label = torch.tensor(self.labels[i], dtype = torch.long)
        
        return img, label

    def __len__(self):
        return len(self.images)

class HTDataset(torch.utils.data.dataset.Dataset):
    """Loading data from input file formatted as csv.
    """
    def __init__(self, image_file, antibody_file, image_tfs=None, expression_tfs=None):
        self.image_tfs = image_tfs
        self.expression_tfs = expression_tfs
        
        df = pd.read_csv(image_file)
        self.images = df['image_name'].to_list()
        self.labels = df['label'].to_list()
        
        df = pd.read_csv(antibody_file)
        self.x = np.asarray(df.loc[:,["Tg","Anti-TG","Anti-TPO","T3","T4","TSH"]])
        self.x = torch.as_tensor(self.x, dtype=torch.float32)
        self.y = np.asarray(df['hashimoto_thyroiditis'])
   
        assert len(np.unique(self.labels)) == 2
        assert len(np.unique(self.y)) == 2
        
        self.x_pos = self.x[self.y == 1]
        self.x_neg = self.x[self.y == 0]
        
        self.x_pos_k = len(self.x_pos)
        self.x_neg_k = len(self.x_neg)

    def __getitem__(self, i):
        path = self.images[i]
        
        with open(path, 'rb') as f:
            img = Image.open(f)
            img = img.convert('RGB')
            
        if self.image_tfs is not None:
            img = self.image_tfs(img)

        if self.labels[i] == 1:
            #x = self.x_pos[np.random.choice(self.x_pos_k)]
            x = self.get_permuted_sample(self.x_pos)
        else:
            #x = self.x_neg[np.random.choice(self.x_neg_k)]
            x = self.get_permuted_sample(self.x_neg)
            
        label = torch.tensor(self.labels[i], dtype = torch.long)
        if self.expression_tfs is not None:
            x = self.expression_tfs(x)
        
        return img, x, label

    def __len__(self):
        return len(self.images)

    def get_permuted_sample(self, x):
        if np.random.random_sample() < 0.05:
            return torch.as_tensor(x[np.random.choice(len(x))], dtype=torch.float32)
        else:
            return torch.as_tensor(np.apply_along_axis(np.random.choice, 0, x), dtype=torch.float32)


class SmoothedValue(object):
    """Track a series of values and provide access to smoothed values over a
    window or the global series average.
    """

    def __init__(self, window_size=20, fmt=None):
        if fmt is None:
            fmt = "{median:.4f} ({global_avg:.4f})"
        self.deque = deque(maxlen=window_size)
        self.total = 0.0
        self.count = 0
        self.fmt = fmt

    def update(self, value, n=1):
        self.deque.append(value)
        self.count += n
        self.total += value * n

    def synchronize_between_processes(self):
        """
        Warning: does not synchronize the deque!
        """
        if not is_dist_avail_and_initialized():
            return
        t = torch.tensor([self.count, self.total], dtype=torch.float64, device='cuda')
        dist.barrier()
        dist.all_reduce(t)
        t = t.tolist()
        self.count = int(t[0])
        self.total = t[1]

    @property
    def median(self):
        d = torch.tensor(list(self.deque))
        return d.median().item()

    @property
    def avg(self):
        d = torch.tensor(list(self.deque), dtype=torch.float32)
        return d.mean().item()

    @property
    def global_avg(self):
        return self.total / self.count

    @property
    def max(self):
        return max(self.deque)

    @property
    def value(self):
        return self.deque[-1]

    def __str__(self):
        return self.fmt.format(
            median=self.median,
            avg=self.avg,
            global_avg=self.global_avg,
            max=self.max,
            value=self.value)


class MetricLogger(object):
    def __init__(self, delimiter="\t"):
        self.meters = defaultdict(SmoothedValue)
        self.delimiter = delimiter

    def update(self, **kwargs):
        for k, v in kwargs.items():
            if isinstance(v, torch.Tensor):
                v = v.item()
            assert isinstance(v, (float, int))
            self.meters[k].update(v)

    def __getattr__(self, attr):
        if attr in self.meters:
            return self.meters[attr]
        if attr in self.__dict__:
            return self.__dict__[attr]
        raise AttributeError("'{}' object has no attribute '{}'".format(
            type(self).__name__, attr))

    def __str__(self):
        loss_str = []
        for name, meter in self.meters.items():
            loss_str.append(
                "{}: {}".format(name, str(meter))
            )
        return self.delimiter.join(loss_str)

    def synchronize_between_processes(self):
        for meter in self.meters.values():
            meter.synchronize_between_processes()

    def add_meter(self, name, meter):
        self.meters[name] = meter

    def log_every(self, iterable, print_freq, header=None):
        i = 0
        if not header:
            header = ''
        start_time = time.time()
        end = time.time()
        iter_time = SmoothedValue(fmt='{avg:.4f}')
        data_time = SmoothedValue(fmt='{avg:.4f}')
        space_fmt = ':' + str(len(str(len(iterable)))) + 'd'
        if torch.cuda.is_available():
            log_msg = self.delimiter.join([
                header,
                '[{0' + space_fmt + '}/{1}]',
                'eta: {eta}',
                '{meters}',
                'time: {time}',
                'data: {data}',
                'max mem: {memory:.0f}'
            ])
        else:
            log_msg = self.delimiter.join([
                header,
                '[{0' + space_fmt + '}/{1}]',
                'eta: {eta}',
                '{meters}',
                'time: {time}',
                'data: {data}'
            ])
        MB = 1024.0 * 1024.0
        for obj in iterable:
            data_time.update(time.time() - end)
            yield obj
            iter_time.update(time.time() - end)
            if i % print_freq == 0:
                eta_seconds = iter_time.global_avg * (len(iterable) - i)
                eta_string = str(datetime.timedelta(seconds=int(eta_seconds)))
                if torch.cuda.is_available():
                    print(log_msg.format(
                        i, len(iterable), eta=eta_string,
                        meters=str(self),
                        time=str(iter_time), data=str(data_time),
                        memory=torch.cuda.max_memory_allocated() / MB))
                else:
                    print(log_msg.format(
                        i, len(iterable), eta=eta_string,
                        meters=str(self),
                        time=str(iter_time), data=str(data_time)))
            i += 1
            end = time.time()
        total_time = time.time() - start_time
        total_time_str = str(datetime.timedelta(seconds=int(total_time)))
        print('{} Total time: {}'.format(header, total_time_str))


def accuracy(output, target, topk=(1,)):
    """Computes the accuracy over the k top predictions for the specified values of k"""
    with torch.no_grad():
        maxk = max(topk)
        batch_size = target.size(0)

        _, pred = output.topk(maxk, 1, True, True)
        pred = pred.t()
        correct = pred.eq(target[None])

        res = []
        for k in topk:
            correct_k = correct[:k].flatten().sum(dtype=torch.float32)
            res.append(correct_k * (100.0 / batch_size))
        return res


def mkdir(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def setup_for_distributed(is_master):
    """
    This function disables printing when not in master process
    """
    import builtins as __builtin__
    builtin_print = __builtin__.print

    def print(*args, **kwargs):
        force = kwargs.pop('force', False)
        if is_master or force:
            builtin_print(*args, **kwargs)

    __builtin__.print = print


def is_dist_avail_and_initialized():
    if not dist.is_available():
        return False
    if not dist.is_initialized():
        return False
    return True


def get_world_size():
    if not is_dist_avail_and_initialized():
        return 1
    return dist.get_world_size()


def get_rank():
    if not is_dist_avail_and_initialized():
        return 0
    return dist.get_rank()


def is_main_process():
    return get_rank() == 0


def save_on_master(*args, **kwargs):
    if is_main_process():
        torch.save(*args, **kwargs)


def init_distributed_mode(args):
    if 'RANK' in os.environ and 'WORLD_SIZE' in os.environ:
        args.rank = int(os.environ["RANK"])
        args.world_size = int(os.environ['WORLD_SIZE'])
        args.gpu = int(os.environ['LOCAL_RANK'])
    elif 'SLURM_PROCID' in os.environ:
        args.rank = int(os.environ['SLURM_PROCID'])
        args.gpu = args.rank % torch.cuda.device_count()
    elif hasattr(args, "rank"):
        pass
    else:
        print('Not using distributed mode')
        args.distributed = False
        return

    args.distributed = True

    torch.cuda.set_device(args.gpu)
    args.dist_backend = 'nccl'
    print('| distributed init (rank {}): {}'.format(
        args.rank, args.dist_url), flush=True)
    torch.distributed.init_process_group(backend=args.dist_backend, init_method=args.dist_url,
                                         world_size=args.world_size, rank=args.rank)
    setup_for_distributed(args.rank == 0)
