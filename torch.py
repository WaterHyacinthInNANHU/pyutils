import random

import numpy as np
import torch
# from tensorboardX import SummaryWriter
from torch.utils.tensorboard import SummaryWriter

def set_seed(seed):
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    random.seed(seed)
    torch.backends.cudnn.deterministic = True


def visualize_module(module, sample_data, save_path = './log'):
    with SummaryWriter(save_path, comment="sample_model_visualization") as sw:
        sw.add_graph(module, sample_data)
