#!/usr/bin/env python
import argparse
import sys
import torch

from txgnn import TxData, TxGNN, TxEval

def parse_args():
    p = argparse.ArgumentParser(description='Train/eval TxGNN on a prepared subgraph folder')
    p.add_argument('--data', required=True, help='Path to subgraph data folder')
    p.add_argument('--device', default=None, help="cpu | cuda:0 | auto (default: auto)")
    p.add_argument('--seed', type=int, default=42)
    p.add_argument('--pretrain-epochs', type=int, default=1)
    p.add_argument('--pretrain-lr', type=float, default=1e-3)
    p.add_argument('--pretrain-batch', type=int, default=512)
    p.add_argument('--finetune-epochs', type=int, default=30)
    p.add_argument('--finetune-lr', type=float, default=5e-4)
    p.add_argument('--train-print-n', type=int, default=10)
    p.add_argument('--valid-every-n', type=int, default=10)
    p.add_argument('--save-name', default='./finetune_subgraph.pt')
    # small model dims for free Colab/CPU
    p.add_argument('--n-hid', type=int, default=64)
    p.add_argument('--n-inp', type=int, default=64)
    p.add_argument('--n-out', type=int, default=64)
    p.add_argument('--proto', action='store_true', default=True)
    p.add_argument('--proto-num', type=int, default=2)
    p.add_argument('--no-attn', action='store_true', help='disable attention (default on)')
    p.add_argument('--sim', default='all_nodes_profile')
    p.add_argument('--agg', default='rarity')
    p.add_argument('--num-walks', type=int, default=50)
    p.add_argument('--path-length', type=int, default=2)
    return p.parse_args()

def main():
    args = parse_args()

    if args.device in (None, 'auto'):
        device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
    else:
        device = args.device

    print('Device:', device)
    print('Data folder:', args.data)

    # Load data & (re)prepare the split (safe to call repeatedly)
    txd = TxData(data_folder_path=args.data)
    txd.prepare_split(split='full_graph', seed=args.seed)

    # Build model
    tx = TxGNN(
        data=txd,
        weight_bias_track=False,
        proj_name='TxGNN',
        exp_name='subgraph_cli',
        device=device,
    )

    tx.model_initialize(
        n_hid=args.n_hid, n_inp=args.n_inp, n_out=args.n_out,
        proto=args.proto, proto_num=args.proto_num,
        attention=not args.no_attn,
        sim_measure=args.sim,
        agg_measure=args.agg,
        num_walks=args.num_walks,
        path_length=args.path_length,
    )

    # Optional pretrain
    if args.pretrain_epochs > 0:
        print('Pretraining...')
        tx.pretrain(
            n_epoch=args.pretrain_epochs,
            learning_rate=args.pretrain_lr,
            batch_size=args.pretrain_batch,
            train_print_per_n=args.train_print_n,
        )
    else:
        print('Skipping pretrain.')

    # Finetune on drug–disease
    print('Finetuning...')
    tx.finetune(
        n_epoch=args.finetune_epochs,
        learning_rate=args.finetune_lr,
        train_print_per_n=args.train_print_n,
        valid_per_n=args.valid_every_n,
        save_name=args.save_name,
    )
    print('Saved finetuned weights to:', args.save_name)

    # Evaluate
    print('Evaluating (disease-centric)...')
    txe = TxEval(model=tx)
    res = txe.eval_disease_centric(
        disease_idxs='test_set',
        show_plot=False,
        verbose=True,
        save_result=True,
        return_raw=False,
        save_name='./eval_subgraph_cli'
    )
    print('Evaluation summary:')
    print(res)

if __name__ == '__main__':
    sys.exit(main())
