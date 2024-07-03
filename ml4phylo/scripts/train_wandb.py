import argparse
from contextlib import nullcontext
import copy
import functools
import math
import numpy as np
import os
from data import TensorDataset
from metrics import MAE, MRE
from model import AttentionNet
from training import init_training, load_checkpoint, save_checkpoint
import random
import torch
from torch.cuda.amp import GradScaler, autocast
from torch.utils.data import DataLoader
from tqdm.auto import tqdm
import wandb
import yaml
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


def train(device: str, wandb_mode: str, in_dir: str, out_dir: str):
    with wandb.init(mode=wandb_mode) as wandb_run:
        config = wandb_run.config
        
        # set seed
        torch.manual_seed(config.seed)
        torch.cuda.manual_seed(config.seed)

        # load dataset
        dataset = os.path.join(in_dir, config.dataset)
        tensor_files = list(os.listdir(dataset))
        n_tensors = int(len(tensor_files) * (1 - config.train_fraction))
        sampled_indices = set(random.Random(config.seed).sample(range(len(tensor_files)), n_tensors))
        train_ids, val_ids = [], []
        for i, file in enumerate(tensor_files):
            val_ids.append(file) if i in sampled_indices else train_ids.append(file)
        train_data = DataLoader(TensorDataset(dataset, filter=train_ids), batch_size=config.batch_size)
        val_data = DataLoader(TensorDataset(dataset, filter=val_ids), batch_size=config.batch_size)
        
        train_batch_log_frequency = int(1 / config.train_batch_logs_per_epoch) if config.train_batch_logs_per_epoch != 0 else float('inf')
        validation_batch_log_frequency = int(1 / config.validation_batch_logs_per_epoch) if config.validation_batch_logs_per_epoch != 0 else float('inf')

        # load model
        if config.checkpoint:
            model, optimizer, scheduler, criterion, _ = load_checkpoint(config.checkpoint, device=device)
        else:
            in_channels, data_len, n_data = train_data.dataset[0][0].shape
            model = AttentionNet(
                in_channels=in_channels, data_len=data_len, n_data=n_data,
                device=device, 
                n_blocks=config.n_blocks, n_heads=config.n_heads, h_dim=config.h_dim, dropout=config.dropout
            )
            model.to(device)
            optimizer, scheduler, criterion = init_training(
                model=model, 
                optimizer=config.optimizer, learning_rate=config.learning_rate, 
                loss=config.criterion
            )
        
        # train and validation loop
        output = os.path.join(out_dir, wandb_run.sweep_id)
        if not os.path.exists(output):
            os.makedirs(output)
        identifier = wandb_run.id
        checkpoint_path = os.path.join(output, f"{identifier}.checkpoint.pt")
        best_path = os.path.join(output, f"{identifier}.best_checkpoint.pt")

        wandb_run.define_metric('train/epoch')
        wandb_run.define_metric('train/epoch-loss', step_metric='train/epoch')
        wandb_run.define_metric('train/batch')
        wandb_run.define_metric('train/batch-loss', step_metric='train/batch')
        wandb_run.define_metric('validation/epoch')
        wandb_run.define_metric('validation/epoch-loss', step_metric='validation/epoch')
        wandb_run.define_metric('validation/epoch-mae', step_metric='validation/epoch')
        wandb_run.define_metric('validation/epoch-mre', step_metric='validation/epoch')
        wandb_run.define_metric('validation/batch')
        wandb_run.define_metric('validation/batch-loss', step_metric='validation/batch')
        wandb_run.define_metric('validation/batch-mae', step_metric='validation/batch')
        wandb_run.define_metric('validation/batch-mre', step_metric='validation/batch')

        if 'cuda' in device:
            scaler = GradScaler()
        
        no_improvement_counter = 0
        best_model = copy.deepcopy(model)
        best_loss = None
        model = model.to(device)
        train_losses, val_losses = [], []
        val_MAEs, val_MREs = [], []

        for epoch in range(config.epochs):
            print()

            # TRAIN STEP
            model.train()
            epoch_train_losses = []
            progress = tqdm(train_data, desc=f'epoch [{epoch+1}/{config.epochs}]')
            for batch, data in enumerate(progress):
                x_train, y_train = data
                x_train, y_train = x_train.to(device), y_train.to(device)
                inputs = x_train.float()

                with (autocast() if 'cuda' in device and config.amp else nullcontext()):
                    optimizer.zero_grad()
                    outputs = model(inputs)
                    y_train = torch.squeeze(y_train.type_as(outputs))
                    train_loss = criterion(outputs, y_train)
                    if 'cuda' in device and config.amp:
                        scaler.scale(train_loss).backward()
                        if config.clip_gradients:
                            scaler.unscale_(optimizer)
                            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=2, error_if_nonfinite=False)
                        scaler.step(optimizer)
                        scaler.update()
                    else:
                        train_loss.backward()
                        optimizer.step()
                
                batch_loss = train_loss.item()
                epoch_train_losses.append(batch_loss)
                progress.set_postfix({'train/batch-loss': f'{batch_loss:.4f}'})
                if (batch % train_batch_log_frequency) == 0 or (batch + 1) == len(train_data):
                    wandb_run.log({'train/batch-loss': batch_loss, 'train/batch': batch + (len(train_data) * epoch)})
                
                # early stop
                if not math.isfinite(batch_loss):
                    progress.close()
                    print(f'ERROR: {batch_loss} train/batch-loss in epoch {epoch} batch {batch}, early stop triggered')
                    print()
                    return

            epoch_loss = np.mean(epoch_train_losses)
            train_losses.append(epoch_loss)
            print(f'epoch [{epoch+1}/{config.epochs}]: train/epoch-loss={epoch_loss:.4f}')
            wandb_run.log({'train/epoch-loss': epoch_loss, 'train/epoch': epoch})

            # VALIDATION STEP
            with torch.no_grad():
                epoch_MAEs, epoch_MREs, epoch_val_losses = [], [], []
                progress = tqdm(val_data, desc=f'epoch [{epoch+1}/{config.epochs}]')
                for batch, data in enumerate(progress):
                    x_val, y_val = data
                    x_val, y_val = x_val.to(device), y_val.to(device)

                    model.eval()
                    inputs = x_val.float()
                    with (autocast() if 'cuda' in device and config.amp else nullcontext()):
                        outputs = model(inputs)
                        y_val = torch.squeeze(y_val.type_as(outputs))
                        val_loss = criterion(outputs, y_val).item()
                        val_MAE = MAE(outputs, y_val)
                        val_MRE = MRE(outputs, y_val)

                    epoch_val_losses.append(val_loss)
                    epoch_MAEs.append(val_MAE)
                    epoch_MREs.append(val_MRE)

                    progress.set_postfix({'validation/batch-loss': f'{val_loss:.4f}'})
                    if (batch % validation_batch_log_frequency) == 0 or (batch + 1) == len(val_data):
                        wandb_run.log({'validation/batch-loss': val_loss, 
                                       'validation/batch': batch + (len(val_data) * epoch), 
                                       'validation/batch-mae': val_MAE, 
                                       'validation/batch-mre': val_MRE})

            val_losses.append(np.mean(epoch_val_losses))
            val_MAEs.append(np.mean(epoch_MAEs))
            val_MREs.append(np.mean(epoch_MREs))
            print(f'epoch [{epoch+1}/{config.epochs}]: validation/epoch-loss={val_losses[-1]:.4f}')
            print(f'epoch [{epoch+1}/{config.epochs}]: validation/epoch-mae={val_MAEs[-1]:.4f}')
            print(f'epoch [{epoch+1}/{config.epochs}]: validation/epoch-mre={val_MREs[-1]:.4f}')
            wandb_run.log({'validation/epoch-loss': val_losses[-1], 
                           'validation/epoch': epoch, 
                           'validation/epoch-mae': val_MAEs[-1], 
                           'validation/epoch-mre': val_MREs[-1]})

            scheduler.step(val_losses[-1])


            if epoch == 0:
                best_loss = val_losses[-1]

            # Save checkpoint
            if checkpoint_path is not None:
                save_checkpoint(model, optimizer, scheduler, dict(config), checkpoint_path)

            # Check if best model so far
            if epoch > 0 and val_losses[-1] < best_loss:
                no_improvement_counter = 0
                best_loss = val_losses[-1]
                best_model = copy.deepcopy(model)
                if best_path is not None:
                    save_checkpoint(model, optimizer, scheduler, dict(config), best_path)
            else:
                no_improvement_counter += 1

            # Stop early if validation loss has not improved for a while
            if (config.early_stopping and no_improvement_counter > config.stopping_steps) or math.isnan(val_losses[-1]):
                return best_model, epoch + 1
        
        return best_model, config.epochs

WANDB_LOGGING_MODES = ['online', 'offline', 'disabled']

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-c',
        '--config',
        default=['config.yaml', '1'], 
        nargs=2, 
        required=False, 
        help='{<yaml sweep config filepath>, <wandb sweep author/project/id>} <number of runs>'
    )
    parser.add_argument(
        '-d', 
        '--device', 
        default='cpu', 
        type=str, 
        required=False, 
        help='<torch device>'
    )
    parser.add_argument(
        '-w', 
        '--wandb', 
        default='online', 
        choices= WANDB_LOGGING_MODES,
        type=str, 
        required=False, 
        help=f'WandB logging mode. Choices: {WANDB_LOGGING_MODES}'
    )
    parser.add_argument(
        "-i",
        "--input",
        required=True,
        type=str,
        help="/path/ to input directory containing the\
    the tensor pairs on which the model will be trained",
    )
    parser.add_argument(
        "-o",
        "--output",
        required=True,
        type=str,
        help="/path/ to output directory where the model parameters\
        and the metrics will be saved",
    )
    args = parser.parse_args()

    wandb.login()
    sweep_id = wandb.sweep(sweep=yaml.load(open(args.config[0], 'r'), Loader)) if args.config[0].split('.')[-1] in ['yaml', 'yml'] else args.config[0]
    sweep_agent_function = functools.partial(train, args.device, args.wandb, args.input, args.output)
    wandb.agent(sweep_id=sweep_id, function=sweep_agent_function, count=int(args.config[1]))


if __name__ == '__main__':
    main()